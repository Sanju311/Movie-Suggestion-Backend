import pandas as pd
from xgboost import XGBRegressor
import ast
import time

'''
Data Pre Processing Formats Required:
    genre -> multi hot-code encoding ex [1 0 0 1 0]
        - each genre must be a seperate feature    
    release date -> [year]
    runtime -> int minutes  
    public rating -> float 
    user rating -> float
    budget -> float 
s'''


#grid seach xgboost model for movie rating prediction
def train_model(user_rated_movies_output, tuning_mode = False):
    
    start_time = time.time()
    
    # Select relevant features and target
    #TODO: Get remaining features
    #features = ['budget', 'genre_encoding', 'runtime', 'release_year', 'vote_average', 'parents_rating', 'plot_vector']
    features = ['budget', 'runtime', 'Release_year', 'vote_average', 'parents_rating']
    target = 'Owner_rating'

    #Film_title,Release_year,Owner_rating,Description,ID,budget,genres,genre_encoding,runtime,vote_average,parents_rating


    # Convert genre_encoding from string to list
    def safe_literal_eval(val):
        
        if isinstance(val, list):
            return val
        elif isinstance(val, str):
            try:
                return ast.literal_eval(val)
            except (ValueError, SyntaxError):
                print(f"Failed to evaluate {val}")
                print(ValueError, SyntaxError)
                return [0] * 18
            
            
    user_rated_movies_output['genre_encoding'] = user_rated_movies_output['genre_encoding'].apply(safe_literal_eval)

    # Drop rows with null values or NoneType objects
    #print(f"length before removing nulls: {len(user_rated_movies_output)}")
    user_rated_movies_output = user_rated_movies_output.dropna()
    user_rated_movies_output = user_rated_movies_output[user_rated_movies_output['budget'] != 0.0]
    #print(f"length after removing any null or 0 values: {len(user_rated_movies_output)}")

    # Expand list into multiple columns
    genre_cols = [f'genre_{i}' for i in range(18)]
    genre_df = pd.DataFrame(user_rated_movies_output['genre_encoding'].tolist(), columns=genre_cols)

    # Drop original genre_encoding column and concatenate expanded columns
    user_rated_movies_output = user_rated_movies_output.drop(columns=['genre_encoding']).reset_index(drop=True)
    user_rated_movies_output = pd.concat([user_rated_movies_output, genre_df], axis=1)
    
    user_rated_movies_output['Release_year'] = pd.to_numeric(user_rated_movies_output['Release_year'], errors='coerce')
    user_rated_movies_output['vote_average'] = pd.to_numeric(user_rated_movies_output['vote_average'], errors='coerce')
    user_rated_movies_output['parents_rating'] = pd.to_numeric(user_rated_movies_output['parents_rating'], errors='coerce')
    user_rated_movies_output['budget'] = pd.to_numeric(user_rated_movies_output['budget'], errors='coerce')
    user_rated_movies_output['runtime'] = pd.to_numeric(user_rated_movies_output['runtime'], errors='coerce')
    user_rated_movies_output['Owner_rating'] = pd.to_numeric(user_rated_movies_output['Owner_rating'], errors='coerce')

    features = features + genre_cols
   
    # for index, row in user_rated_movies_output.iterrows():
    #     print(row['genre_encoding'])

    # Ensure other features are numeric
    #user_rated_movies_output[features] = user_rated_movies_output[features].apply(pd.to_numeric, errors='coerce')

    # Create feature matrix (X) and target vector (y)
    X = user_rated_movies_output[features]
    y = user_rated_movies_output[target]
    
    # Combine the feature matrix (X) and target vector (y) into a single DataFrame
    data_to_save = X.copy()
    data_to_save[target] = y

    # Write the combined DataFrame to a CSV file
    #data_to_save.to_csv('TRAINING_DATA.csv', index=False)
    
    
    if not tuning_mode:
        
        try:
            #Define the parameter grid
            param_grid = {
                'n_estimators': 100,
                'max_depth': 3,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'min_child_weight': 3
            }

            #Create the model
            model = XGBRegressor(**param_grid, random_state=42, enable_categorical=True) 
            model.fit(X, y)
            
            #return trained model
            return model
        except Exception as e:
            print(e)
            return {"Failed to train model"}, 500
    else:
    
        from sklearn.model_selection import GridSearchCV
        from sklearn.model_selection import train_test_split, KFold
        from sklearn.metrics import root_mean_squared_error

        #Define the XGBRegressor model
        model = XGBRegressor(random_state=42)
        
        param_grid = {
            'n_estimators': [50, 100, 200],          # Number of trees in the ensemble
            'max_depth': [3, 4, 5],                 # Maximum depth of each tree
            'learning_rate': [0.01, 0.05, 0.1],     # Step size shrinkage
            'subsample': [0.6, 0.8, 1.0],           # Fraction of samples used for training each tree
            'colsample_bytree': [0.6, 0.8, 1.0],    # Fraction of features used per tree
            'min_child_weight': [1, 3, 5],          # Minimum sum of weights required in a child node
            'gamma': [0, 0.1, 0.3],                 # Minimum loss reduction required to make a split
            'reg_alpha': [0, 0.01, 0.1],            # L1 regularization (weight penalties)
            'reg_lambda': [1, 1.5, 2],              # L2 regularization (weight penalties)
        }

        #Set up GridSearchCV
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            scoring='neg_root_mean_squared_error',  # Use RMSE as the scoring metric
            cv=5,  # 5-fold cross-validation
            verbose=1,
            n_jobs=-1  # Use all available cores
        )
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print("performing grid search...")

        #Perform the grid search
        grid_search.fit(X_train, y_train)

        #Print the best parameters and RMSE
        print("Best Parameters:", grid_search.best_params_)
        print("Best RMSE:", -grid_search.best_score_)  # Negated because RMSE is negative in scoring

        tuned_model = XGBRegressor(**param_grid, random_state=42)
        
        #Perform K-Fold Cross-Validation
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_rmse = []

        for train_index, val_index in kf.split(X):
            X_train_kf, X_val_kf = X.iloc[train_index], X.iloc[val_index]
            y_train_kf, y_val_kf = y.iloc[train_index], y.iloc[val_index]
            
            tuned_model.fit(X_train_kf, y_train_kf)
            y_val_pred = tuned_model.predict(X_val_kf)
            fold_rmse = root_mean_squared_error(y_val_kf, y_val_pred)
            cv_rmse.append(fold_rmse)
            print(f"Fold RMSE: {fold_rmse:.2f}")

        print(f"Mean Cross-Validation RMSE: {sum(cv_rmse) / len(cv_rmse):.2f}")
