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

MODEL_PATH = os.path.join(settings.BASE_DIR, 'svm_model (1).pkl')
def get_predictions(request):
    try:
        # Connect to the database and execute the query
        with connection.cursor() as cursor:
            cursor.execute("USE whole_proj;")
            cursor.execute("""
                SELECT stu.email, sess.arousal, sess.attention, sess.valence, sess.volume, qa.timestart, qa.timefinish, qa.sumgrades
                FROM Session sess
                JOIN Students stu ON sess.userEmail = stu.email
                JOIN Quiz_Attempts qa ON stu.id = qa.userid
                JOIN Quiz q ON qa.quiz = q.id
                WHERE qa.quiz = '18';
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = pd.DataFrame(rows, columns=columns)
        
        # Preprocess the data
        data['sec'] = (data['timefinish'] - data['timestart']).abs()

        # Select specific columns to keep
        columns_to_keep_from_quiz = ['sumgrades', 'sec', 'email']
        data_quiz = data[columns_to_keep_from_quiz]

        # Convert 'sumgrades' and 'sec' columns to numeric, coercing errors to NaN
        data_quiz[['sumgrades', 'sec']] = data_quiz[['sumgrades', 'sec']].apply(pd.to_numeric, errors='coerce')

        # Filter out non-numeric rows in the last two columns
        data_quiz[['sumgrades', 'sec']] = data_quiz[['sumgrades', 'sec']].applymap(lambda x: x if isinstance(x, (int, float)) else pd.NA)

        # Create a new column that is the sum of the last two columns
        data_quiz['grade_and_time'] = data_quiz[['sumgrades', 'sec']].sum(axis=1)

        # Preprocess session data
        columns_to_keep = ['email', 'arousal', 'attention', 'valence', 'volume']
        data_sessions = data[columns_to_keep]

        # Group by 'userEmail'
        grouped = data_sessions.groupby('email')

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
            median_group = data_sessions[data_sessions['email'].isin(non_normal_users)]
            median_agg = median_group.groupby('email').agg({
                'arousal': ['min', 'max', 'median'],  # Use 'median'
                'attention': ['min', 'max', 'median'],
                'valence': ['min', 'max', 'median'],
                'volume': ['min', 'max', 'median']
            })
            median_agg.columns = ["_".join(x) for x in median_agg.columns.ravel()]

        # Calculate summary statistics for normal users
        mean_agg = pd.DataFrame()
        if normal_users:
            mean_group = data_sessions[data_sessions['email'].isin(normal_users)]
            mean_agg = mean_group.groupby('email').agg({
                'arousal': ['min', 'max', 'mean'],  # Use 'mean'
                'attention': ['min', 'max', 'mean'],
                'valence': ['min', 'max', 'mean'],
                'volume': ['min', 'max', 'mean']
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

        # Merge the processed data_quiz with combined_agg on 'email' and 'email' respectively
        combined_data = pd.merge(data_quiz, combined_agg, left_on='email', right_on='email', how='inner')

        combined_data = combined_data.drop_duplicates(subset='email')

        # Load the trained model from the pkl file
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)

        # Load your new data from the Excel file
        new_data = combined_data

        # Drop rows with all null values
        new_data = new_data.dropna(axis=0, how='all')

        # Drop rows with any null values
        new_data = new_data.dropna()

        # Check if there are any rows left after dropping null values
        if new_data.shape[0] == 0:
            return JsonResponse({"error": "No data available after dropping rows with null values."}, status=400)

        # Define the features to use for prediction
        features_to_use = ['grade_and_time', 'arousal_min', 'arousal_max', 'attention_min', 'attention_max',
                           'valence_max', 'valence_min', 'volume_min', 'volume_max', 'arousal', 'attention',
                           'valence', 'volume']

        # Select the features
        features = new_data[features_to_use]

        # Scale the features using MinMaxScaler
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)

        # Make predictions using the loaded model
        predictions = model.predict(scaled_features)

        # Add predictions to the original new_data DataFrame
        new_data['predictions'] = predictions

        # Convert the DataFrame to a list of dictionaries with proper formatting
        result = new_data.to_dict(orient='records')

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)