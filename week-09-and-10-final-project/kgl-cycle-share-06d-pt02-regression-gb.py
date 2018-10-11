## ######################################################################### ##
## Analysis of 
## For EdX Course
## Python for Data Science (Week 9 and 10 Final Project)
## ######################################################################### ##

## Classification first, then regression

## ========================================================================= ## 
## import libraries
## ========================================================================= ##

## ========================================================================= ##
## modeling number of trips (non-zero trips only)
## ========================================================================= ##

## ------------------------------------------------------------------------- ##
## restrict data
## ------------------------------------------------------------------------- ##

## [[?]] better way to subset pandas dataframe?
dat_hr_nonzerotrips = dat_hr_all[dat_hr_all["trip_cnt"] > 0]

#dat_hr_all.shape
#dat_hr_nonzerotrips.shape
#dat_hr_nonzerotrips.head()

## ------------------------------------------------------------------------- ##
## define features and formula
## ------------------------------------------------------------------------- ##

## convert categorical variables to strings
## (in order for patsy to automatically dummy-code them without
## having to use the C() function):

# dat_hr_all['Month'] = dat_hr_all['Month'].astype('str')
# dat_hr_all['hr_of_day'] = dat_hr_all['hr_of_day'].astype('str')

## interesting:
## accuracy seems to be higher for non-categorical features!

## define target and features:
target = 'trip_cnt'
features = ['Month',
            'Temp (°C)',
            # 'Dew Point Temp (°C)', ## -- exclude, because highly correlated with Temp
            'Rel Hum (%)',
            'Wind Dir (10s deg)',
            'Wind Spd (km/h)',
            'Stn Press (kPa)',
            'hr_of_day',
            'day_of_week']
list(dat_hr_all)

## add patsy-quoting to features (for weird column names):
target = 'Q(\'' + target + '\')' 
features = ['Q(\'' + i + '\')' for i in features]

## formula as text for patsy: without interactions
formula_txt = target + ' ~ ' + \
    ' + '.join(features) + ' - 1'
formula_txt

# ## try all twofold interactions, in order to 
# ## find important ones via variable importance plots:
# formula_txt = target + ' ~ (' + ' + '.join(features) + ') ** 2 - 1'
# formula_txt

## create design matrices using patsy (could directly be used for modeling):
#patsy.dmatrix?
dat_y, dat_x = patsy.dmatrices(formula_txt, dat_hr_nonzerotrips, 
                               NA_action = 'drop',
                               return_type = 'dataframe')
dat_x.head()

## other possibilities for dummy coding:
## * pd.get_dummies [[?]] which to use?

## ------------------------------------------------------------------------- ##
## train / test split
## ------------------------------------------------------------------------- ##

## Split the data into training/testing sets (using patsy/dmatrices):
dat_train_x, dat_test_x, dat_train_y, dat_test_y = train_test_split(
    dat_x, dat_y, test_size = 0.20, random_state = 142)

## convert y's to Series (to match data types between patsy and non-patsy data prep:)
dat_train_y = dat_train_y[target]
dat_test_y = dat_test_y[target]

#dat_train_x.shape
#dat_test_x.shape

## ------------------------------------------------------------------------- ##
## normalize data
## ------------------------------------------------------------------------- ##

## [[todo]]


## ------------------------------------------------------------------------- ##
## estimate model and evaluate fit and model assumptions
## ------------------------------------------------------------------------- ##

## Instantiate random forest estimator:
mod_gb = GradientBoostingRegressor(n_estimators = 100, 
                                   random_state = 42,
                                   loss = 'ls',
                                   learning_rate = 0.1,
                                   max_depth = 20, 
                                   min_samples_split = 70,
                                   min_samples_leaf = 30,
                                   verbose = 1)

## Train the model using the training sets:
mod_gb.fit(dat_train_x, dat_train_y)

## [[?]] missing: how to plot oob error by number of trees, like in R?
    
## Make predictions using the testing set
dat_test_pred = mod_gb.predict(dat_test_x)
dat_train_pred = mod_gb.predict(dat_train_x)

## Inspect model:
mean_squared_error(dat_train_y, dat_train_pred)  # MSE in training set
mean_squared_error(dat_test_y, dat_test_pred)    # MSE in test set
mean_absolute_error(dat_train_y, dat_train_pred)  # MAE in training set
mean_absolute_error(dat_test_y, dat_test_pred)    # MAE in test set
r2_score(dat_train_y, dat_train_pred)            # R^2 (r squared) in test set
r2_score(dat_test_y, dat_test_pred)              # R^2 (r squared) in test set

## ------------------------------------------------------------------------- ##
## save model to disk
## ------------------------------------------------------------------------- ##

## [[?]] who to persist models?
## * don't use pickle or joblib (unsafe and not persistent)
##   see https://pyvideo.org/pycon-us-2014/pickles-are-for-delis-not-software.html or
##   http://scikit-learn.org/stable/modules/model_persistence.html
##   (3.4.2. Security & maintainability limitations)

from sklearn.externals import joblib

# model_name = 
filename_model = 'model_nonzero_gradient_boosting.pkl'
joblib.dump(mod_gb, os.path.join(path_out, filename_model))

# ## load:
# filename_model = 'model_gradient_boosting.pkl'
# mod_this = joblib.load(os.path.join(path_out, filename_model))

