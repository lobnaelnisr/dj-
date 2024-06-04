from django.shortcuts import render
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
from django.http import JsonResponse
import scipy.stats as stats
import os
from django.conf import settings
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from project2.settings import BASE_DIR

# Define the path to the model
MODEL_PATH = os.path.join(BASE_DIR, 'svm_model (1).pkl')

@csrf_exempt
@api_view(['GET'])
def get_predictions(request):
    try:
        # Load the trained model from the pkl file
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)

        with connection.cursor() as cursor:
            cursor.execute("USE whole_proj;")
            cursor.execute("""                    
                SELECT stu.email, sess.arousal, sess.attention, sess.valence, sess.volume, qa.timestart, qa.timefinish, qa.sumgrades
                FROM Session sess
                JOIN Students stu ON sess.userEmail = stu.email
                JOIN Quiz_Attempts qa ON stu.id = qa.userid
                JOIN Quiz q ON qa.quiz = q.id
                WHERE qa.quiz = '19';
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = pd.DataFrame(rows, columns=columns)
        
        # Debugging: Log the columns present in the fetched data
        print("Fetched Data Columns:", data.columns.tolist())

        # Calculate 'sec' as the absolute difference between 'timefinish' and 'timestart'
        data['sec'] = (data['timefinish'] - data['timestart']).abs()

        # Select specific columns to keep
        columns_to_keep_from_quiz = ['sumgrades', 'sec', 'email', 'arousal', 'attention', 'valence', 'volume']
        data = data[columns_to_keep_from_quiz]

        # Convert 'sumgrades' and 'sec' columns to numeric, coercing errors to NaN
        data[['sumgrades', 'sec']] = data[['sumgrades', 'sec']].apply(pd.to_numeric, errors='coerce')

        # Filter out non-numeric rows in the last two columns
        data[['sumgrades', 'sec']] = data[['sumgrades', 'sec']].applymap(lambda x: x if isinstance(x, (int, float)) else pd.NA)

        # Create a new column that is the sum of the last two columns
        data['grade_and_time'] = data[['sumgrades', 'sec']].sum(axis=1)

        # Handle missing values before further processing
        data = data.dropna(subset=['sumgrades', 'sec', 'arousal', 'attention', 'valence', 'volume', 'grade_and_time'])

        # Debugging: Log the columns present in the data before analysis
        print("Data Columns before Analysis:", data.columns.tolist())

        # Analyze and process sessions
        processed_data = analyze_and_process_sessions(data)

        # Ensure the required columns are in the processed_data
        required_columns = ['arousal', 'attention', 'valence', 'volume', 'grade_and_time',
                            'arousal_min', 'arousal_max', 'attention_min', 'attention_max', 
                            'valence_min', 'valence_max', 'volume_min', 'volume_max']
        for col in required_columns:
            if col not in processed_data.columns:
                return JsonResponse({"error": f"Column '{col}' not found in processed data."}, status=500)

        # Define the features to scale
        features_to_scale = required_columns
        features = processed_data[features_to_scale]

        # Ensure there are no NA values in features before scaling
        features = features.fillna(0)

        # Scale the features using MinMaxScaler
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)

        # Make predictions using the loaded model
        predictions = model.predict(scaled_features)

        # Add predictions to the processed_data DataFrame
        processed_data['predictions'] = predictions

        # Convert NAType to None for JSON serialization
        processed_data = processed_data.where(pd.notnull(processed_data), None)

        # Create a list of dictionaries with proper formatting
        result = []
        for index, row in processed_data.iterrows():
            result.append({
                "email": row['email'],
                "grade_and_time": row['grade_and_time'],
                "arousal": row['arousal'],
                "attention": row['attention'],
                "valence": row['valence'],
                "volume": row['volume'],
                "predictions": row['predictions']
            })

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def analyze_and_process_sessions(data):
    # Ensure necessary columns are in the input data
    required_columns = ['email', 'arousal', 'attention', 'valence', 'volume', 'grade_and_time']
    if not all(column in data.columns for column in required_columns):
        raise ValueError(f"Input data must contain the following columns: {required_columns}")

    # Group by 'email'
    grouped = data.groupby('email')

    # Lists to categorize users based on normality test
    normal_users = []
    non_normal_users = []

    # Iterate over groups and perform Shapiro-Wilk test
    for name, group in grouped:
        if len(group) >= 3:  # Check if there are enough data points for the test
            shapiro_test = stats.shapiro(group['arousal'])
            p_value = shapiro_test.pvalue

            # Categorize as normal or non-normal
            if p_value < 0.05:
                non_normal_users.append(name)
            else:
                normal_users.append(name)

    # Calculate summary statistics for non-normal users
    median_agg = pd.DataFrame()
    if non_normal_users:
        median_group = data[data['email'].isin(non_normal_users)]
        median_agg = median_group.groupby('email').agg({
            'arousal': ['min', 'max', 'median'],  # Use 'median'
            'attention': ['min', 'max', 'median'],
            'valence': ['min', 'max', 'median'],
            'volume': ['min', 'max', 'median'],
            'grade_and_time': ['median']
        })
        median_agg.columns = ["_".join(x) for x in median_agg.columns.ravel()]

    # Calculate summary statistics for normal users
    mean_agg = pd.DataFrame()
    if normal_users:
        mean_group = data[data['email'].isin(normal_users)]
        mean_agg = mean_group.groupby('email').agg({
            'arousal': ['min', 'max', 'mean'],  # Use 'mean'
            'attention': ['min', 'max', 'mean'],
            'valence': ['min', 'max', 'mean'],
            'volume': ['min', 'max', 'mean'],
            'grade_and_time': ['mean']
        })
        mean_agg.columns = ["_".join(x) for x in mean_agg.columns.ravel()]

    # Combine the median-based and mean-based summaries
    combined_agg = pd.concat([median_agg, mean_agg]).reset_index()

    # Consolidate columns by taking the non-null values and dropping the original columns
    columns_pairs = [
        ['arousal_median', 'arousal_mean'],
        ['attention_median', 'attention_mean'],
        ['valence_median', 'valence_mean'],
        ['volume_median', 'volume_mean']
    ]
    
    for col1, col2 in columns_pairs:
        new_col = col1.split('_')[0]  # Extract the base name for the new column
        # Create the new column by comparing the two columns and taking the non-null value
        combined_agg[new_col] = combined_agg[col1].combine_first(combined_agg[col2])
        # Drop the original columns
        combined_agg.drop(columns=[col1, col2], inplace=True)

    # Ensure the resulting DataFrame contains the necessary columns
    final_columns = ['email', 'arousal', 'attention', 'valence', 'volume', 'grade_and_time',
                     'arousal_min', 'arousal_max', 'attention_min', 'attention_max', 
                     'valence_min', 'valence_max', 'volume_min', 'volume_max']
    for col in final_columns:
        if col not in combined_agg.columns:
            combined_agg[col] = pd.NA
    
    return combined_agg