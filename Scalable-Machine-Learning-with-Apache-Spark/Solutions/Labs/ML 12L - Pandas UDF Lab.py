# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md # Pandas UDF Lab
# MAGIC 
# MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
# MAGIC - Perform model inference at scale using a Pandas UDF created from MLflow

# COMMAND ----------

# MAGIC %run "../Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC In the cell below, we train the same model on the same data set as in the lesson. 

# COMMAND ----------

import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

with mlflow.start_run(run_name="sklearn-random-forest") as run:
    # Import the data
    df = pd.read_csv(f"{datasets_dir}/airbnb/sf-listings/airbnb-cleaned-mlflow.csv".replace("dbfs:/", "/dbfs/"))
    X_train, X_test, y_train, y_test = train_test_split(df.drop(["price"], axis=1), df[["price"]].values.ravel(), random_state=42)

    # Create model, train it, and create predictions
    rf = RandomForestRegressor(n_estimators=100, max_depth=10)
    rf.fit(X_train, y_train)
    predictions = rf.predict(X_test)

    # Log model
    mlflow.sklearn.log_model(rf, "random-forest-model")

    # Log params
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)

    # Log metrics
    mlflow.log_metric("mse", mean_squared_error(y_test, predictions))
    mlflow.log_metric("mae", mean_absolute_error(y_test, predictions))  
    mlflow.log_metric("r2", r2_score(y_test, predictions))  

# COMMAND ----------

# MAGIC %md Let's convert our Pandas DataFrame to a Spark DataFrame for distributed inference.

# COMMAND ----------

spark_df = spark.createDataFrame(df)

# COMMAND ----------

# MAGIC %md ### MLflow UDF
# MAGIC 
# MAGIC Here, instead of using `mlflow.sklearn.load_model(model_path)`, we would like to use `mlflow.pyfunc.spark_udf()`.
# MAGIC 
# MAGIC This method can reduce computational cost and space, since it only loads the model into memory once per Python process. In other words, when we generate predictions for a DataFrame, the Python process knows that it should reuse the copy of the model, rather than loading the same model more than once. This can actually be more performant than using a Pandas Iterator UDF.

# COMMAND ----------

# MAGIC %md
# MAGIC In the cell below, fill in the `model_path` variable and the `mlflow.pyfunc.spark_udf` function. You can refer to this [documentation](https://www.mlflow.org/docs/latest/python_api/mlflow.pyfunc.html#mlflow.pyfunc.spark_udf) for help. 

# COMMAND ----------

# ANSWER

model_path = f"runs:/{run.info.run_id}/random-forest-model"
predict = mlflow.pyfunc.spark_udf(spark, model_path)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC After loading the model using `mlflow.pyfunc.spark_udf`, we can now perform model inference at scale.
# MAGIC 
# MAGIC In the cell below, fill in the blank to use the `predict` function you have defined above to predict the price based on the features.

# COMMAND ----------

# ANSWER

features = X_train.columns
display(spark_df.withColumn("prediction", predict(*features)))

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2021 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>
