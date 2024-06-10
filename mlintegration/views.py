import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
from django.http import JsonResponse
import scipy.stats as stats
import os
from django.conf import settings
from django.db import connection
from rest_framework.decorators import api_view
import sklearn
from sklearn.svm import SVC
from project2.settings import BASE_DIR

MODEL_PATH1 = os.path.join(BASE_DIR, 'svm_model (1).pkl')

@api_view(['GET'])
def get_predictions(request):
    try:
        # Connect to the database and execute the query
        with connection.cursor() as cursor:
            cursor.execute("USE whole_proj;")
            cursor.execute("""
                   SELECT stu.email, sess.arousal, sess.attention, sess.valence, sess.volume, sess.Session_For, c.Course, qa.timestart, qa.timefinish, qa.sumgrades
                   FROM Session sess
                   JOIN Students stu ON sess.userEmail = stu.email
                   JOIN Quiz_Attempts qa ON stu.id = qa.userid
                   JOIN Quiz q ON qa.quiz = q.id
                   JOIN Course c ON q.course = c.id
                   WHERE (c.Course = 'System Analysis & Design' AND sess.Session_For = 'SA-quiz')
                   OR (c.Course = 'Management of Technology' AND sess.Session_For = 'MOT-quiz');
            """)

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = pd.DataFrame(rows, columns=columns)

        # Preprocess the data
        data['sec'] = (data['timefinish'] - data['timestart']).abs()

        # Select specific columns to keep
        columns_to_keep_from_quiz = ['sumgrades', 'sec', 'email', 'Course', 'Session_For']
        data_quiz = data[columns_to_keep_from_quiz]

        # Convert 'sumgrades' and 'sec' columns to numeric, coercing errors to NaN
        data_quiz[['sumgrades', 'sec']] = data_quiz[['sumgrades', 'sec']].apply(pd.to_numeric, errors='coerce')

        # Filter out non-numeric rows in the last two columns
        data_quiz = data_quiz.dropna()

        # Create a new column that is the sum of the last two columns
        data_quiz['grade_and_time'] = data_quiz[['sumgrades', 'sec']].sum(axis=1)

        # Preprocess session data
        columns_to_keep = ['email', 'arousal', 'attention', 'valence', 'volume', 'Course', 'Session_For']
        data_sessions = data[columns_to_keep]

        # Group by 'email', 'Course', and 'Session_For'
        grouped = data_sessions.groupby(['email', 'Course', 'Session_For'])

        # Lists to categorize users based on normality test
        normal_users = []
        non_normal_users = []

        # Iterate over groups and perform Shapiro-Wilk test
        for (email, course, session_for), group in grouped:
            if len(group) >= 3:  # Check if there are enough data points for the test
                shapiro_test = stats.shapiro(group['arousal'])
                p_value = shapiro_test.pvalue

                # Categorize as normal or non-normal
                if p_value < 0.05:
                    non_normal_users.append((email, course, session_for))
                else:
                    normal_users.append((email, course, session_for))

        # Calculate summary statistics for non-normal users
        median_agg = pd.DataFrame()
        if non_normal_users:
            median_group = data_sessions[data_sessions[['email', 'Course', 'Session_For']].apply(tuple, axis=1).isin(non_normal_users)]
            median_agg = median_group.groupby(['email', 'Course', 'Session_For']).agg({
                'arousal': ['min', 'max', 'median'],  # Use 'median'
                'attention': ['min', 'max', 'median'],
                'valence': ['min', 'max', 'median'],
                'volume': ['min', 'max', 'median']
            })
            median_agg.columns = ["_".join(x) for x in median_agg.columns.ravel()]

        # Calculate summary statistics for normal users
        mean_agg = pd.DataFrame()
        if normal_users:
            mean_group = data_sessions[data_sessions[['email', 'Course', 'Session_For']].apply(tuple, axis=1).isin(normal_users)]
            mean_agg = mean_group.groupby(['email', 'Course', 'Session_For']).agg({
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

        # Merge the processed data_quiz with combined_agg on 'email', 'Course', and 'Session_For'
        combined_data = pd.merge(data_quiz, combined_agg, on=['email', 'Course', 'Session_For'], how='inner')

        combined_data = combined_data.drop_duplicates(subset=['email', 'Course', 'Session_For'], keep='last')

        # Define the features to use for prediction
        features_to_use = ['grade_and_time', 'arousal_min', 'arousal_max', 'attention_min', 'attention_max',
                           'valence_max', 'valence_min', 'volume_min', 'volume_max', 'arousal', 'attention',
                           'valence', 'volume']

        # Select the features
        features = combined_data[features_to_use]

        # Scale the features using MinMaxScaler
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)

        # Load the trained model from the pkl file
        if os.path.exists(MODEL_PATH1):
            with open(MODEL_PATH1, 'rb') as file:
                model = pickle.load(file)
        else:
            model = SVC()  # Assuming SVC model, change accordingly
            # Here you should fit your model with your training data.
            # This example assumes a 'target_column' exists. Adjust according to your use case.
            model.fit(scaled_features, combined_data['target_column'])  # Replace 'target_column' with the actual target column name
            with open(MODEL_PATH1, 'wb') as file:
                pickle.dump(model, file)

        
        # Make predictions using the loaded model
        predictions = model.predict(scaled_features)

        # Add predictions to the original combined_data DataFrame
        combined_data['Success_Prediction'] = predictions

        # Insert predictions into the database

        with connection.cursor() as cursor:
            for _, row in combined_data.iterrows():
                cursor.execute("""
                    INSERT INTO Academic_Performance (Email, Course, Session_for, Grades, Success_Prediction)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE Success_Prediction = VALUES(Success_Prediction);
                """, (row['email'], row['Course'], row['Session_For'], row['sumgrades'], row['Success_Prediction']))
        
        # Commit the changes to the database
        connection.commit()


        # Convert the DataFrame to a list of dictionaries with proper formatting
        result = combined_data.to_dict(orient='records')

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

MODEL_PATH2 = os.path.join(settings.BASE_DIR, 'trained_model.pkl')

def get_predictionsforgrades(request=None):
    try:
        # Connect to the database and execute the query
        with connection.cursor() as cursor:
            cursor.execute("USE whole_proj;")
            cursor.execute("""
                SELECT stu.email, sess.arousal, sess.attention, sess.valence, sess.volume, sess.Session_For, c.Course, qa.timestart, qa.timefinish, qa.sumgrades
                FROM Session sess
                JOIN Students stu ON sess.userEmail = stu.email
                JOIN Quiz_Attempts qa ON stu.id = qa.userid
                JOIN Quiz q ON qa.quiz = q.id
                JOIN Course c ON q.course = c.id
                WHERE (c.Course = 'System Analysis & Design' AND sess.Session_For = 'SA-quiz')
                OR (c.Course = 'System Analysis & Design' AND sess.Session_For = 'SA-quiz-2')           
                OR (c.Course = 'Management of Technology' AND sess.Session_For = 'MOT-quiz');
            """)

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = pd.DataFrame(rows, columns=columns)

        # Preprocess the data
        data['sec'] = (data['timefinish'] - data['timestart']).abs()

        # Select specific columns to keep
        columns_to_keep_from_quiz = ['sumgrades', 'sec', 'email', 'Course', 'Session_For']
        data_quiz = data[columns_to_keep_from_quiz]

        # Convert 'sumgrades' and 'sec' columns to numeric, coercing errors to NaN
        data_quiz[['sumgrades', 'sec']] = data_quiz[['sumgrades', 'sec']].apply(pd.to_numeric, errors='coerce')

        # Filter out non-numeric rows in the last two columns
        data_quiz = data_quiz.dropna()

        # Create a new column that is the sum of the last two columns
        data_quiz['grade_and_time'] = data_quiz[['sumgrades', 'sec']].sum(axis=1)

        # Preprocess session data
        columns_to_keep = ['email', 'arousal', 'attention', 'valence', 'volume', 'Course', 'Session_For']
        data_sessions = data[columns_to_keep]

        # Group by 'email', 'Course', and 'Session_For'
        grouped = data_sessions.groupby(['email', 'Course', 'Session_For'])

        # Lists to categorize users based on normality test
        normal_users = []
        non_normal_users = []

        # Iterate over groups and perform Shapiro-Wilk test
        for (email, course, session_for), group in grouped:
            if len(group) >= 3:  # Check if there are enough data points for the test
                shapiro_test = stats.shapiro(group['arousal'])
                p_value = shapiro_test.pvalue

                # Categorize as normal or non-normal
                if p_value < 0.05:
                    non_normal_users.append((email, course, session_for))
                else:
                    normal_users.append((email, course, session_for))

        # Calculate summary statistics for non-normal users
        median_agg = pd.DataFrame()
        if non_normal_users:
            median_group = data_sessions[data_sessions[['email', 'Course', 'Session_For']].apply(tuple, axis=1).isin(non_normal_users)]
            median_agg = median_group.groupby(['email', 'Course', 'Session_For']).agg({
                'arousal': ['min', 'max', 'median'],  # Use 'median'
                'attention': ['min', 'max', 'median'],
                'valence': ['min', 'max', 'median'],
                'volume': ['min', 'max', 'median']
            })
            median_agg.columns = ["_".join(x) for x in median_agg.columns.ravel()]

        # Calculate summary statistics for normal users
        mean_agg = pd.DataFrame()
        if normal_users:
            mean_group = data_sessions[data_sessions[['email', 'Course', 'Session_For']].apply(tuple, axis=1).isin(normal_users)]
            mean_agg = mean_group.groupby(['email', 'Course', 'Session_For']).agg({
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

        # Merge the processed data_quiz with combined_agg on 'email', 'Course', 'Session_For'
        combined_data = pd.merge(data_quiz, combined_agg, on=['email', 'Course', 'Session_For'], how='inner')

        combined_data = combined_data.drop_duplicates(subset=['email', 'Course', 'Session_For'], keep='last')

        # Load the trained model, scaler, imputer, and PCA components from the pkl file
        with open(MODEL_PATH2, 'rb') as file:
            model_data = pickle.load(file)
            model = model_data['model']
            scaler = model_data['scaler']
            imputer = model_data['imputer']
            pca = model_data['pca']
            trained_sklearn_version = model_data.get('sklearn_version', 'unknown')

        # Check sklearn version compatibility
        current_sklearn_version = sklearn.__version__
        if current_sklearn_version != trained_sklearn_version:
            raise ImportError(f"Trained model uses scikit-learn version {trained_sklearn_version}, but current version is {current_sklearn_version}")

        # Define the features to use for prediction
        features_to_use = ['grade_and_time', 'arousal_min', 'arousal_max', 'attention_min', 'attention_max',
                           'valence_max', 'valence_min', 'volume_min', 'volume_max', 'arousal', 'attention',
                           'valence', 'volume']

        # Select the features
        features = combined_data[features_to_use]

        # Handle missing values in features
        features_imputed = imputer.transform(features)

        # Scale the features
        scaled_features = scaler.transform(features_imputed)

        # Apply PCA
        pca_features = pca.transform(scaled_features)

        # Make predictions using the loaded model
        gradepredictions = model.predict(pca_features)

        # Add predictions to the original combined_data DataFrame
        combined_data['Grade_Prediction'] = gradepredictions

        # Insert predictions into the database
        with connection.cursor() as cursor:
            for _, row in combined_data.iterrows():
                cursor.execute("""
                    INSERT INTO Academic_Performance (Email, Course, Session_For, Grades, Grade_Prediction)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE Grade_Prediction = VALUES(Grade_Prediction);
                """, (row['email'], row['Course'], row['Session_For'],row['sumgrades'], row['Grade_Prediction']))

        # Commit the changes to the database
        connection.commit()


        # Convert the DataFrame to a list of dictionaries with proper formatting
        result = combined_data.to_dict(orient='records')

        # If the function is called by a request, return JsonResponse
        if request is not None:
            return JsonResponse(result, safe=False)
        
        # Print the result if called by the scheduler
        print("The Scheduler has fetched the predictions")
        return result

    except Exception as e:
        error_message = {"error": str(e)}
        # If the function is called by a request, return JsonResponse with the error
        if request is not None:
            return JsonResponse(error_message, status=500)
        
        # Print the error if called by the scheduler
        print("Error:", error_message)
        return error_message

# Create a Django view to handle requests for predictions
@api_view(['GET'])
def get_predictions_view(request):
    return get_predictionsforgrades(request)