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
    
    # Load the data
    data = pd.read_csv(user_rated_movies_output)  # Replace "data.csv" with your actual file name

    # Select relevant features and target
    features = ['budget', 'genre_encoding', 'runtime', 'release_year', 'vote_average', 'parents_rating', 'plot_vector']
    target = 'user_rating'

    # Convert genre_encoding from string to list
    data['genre_encoding'] = data['genre_encoding'].apply(ast.literal_eval)
    data['plot_vector'] = data['plot_vector'].apply(ast.literal_eval)
    # Ensure other features are numeric
    data[features] = data[features].apply(pd.to_numeric, errors='coerce')


    # Create feature matrix (X) and target vector (y)
    X = data[features]
    y = data[target]
    
    if not tuning_mode:
        
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
        model = XGBRegressor(**param_grid, random_state=42) 
        model.fit(X, y)
        
        #return trained model
        return model
    
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
            
    # End the timer
    end_time = time.time()
    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Program runtime: {elapsed_time:.2f} seconds")