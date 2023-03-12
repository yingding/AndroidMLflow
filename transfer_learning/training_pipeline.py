from zenml.pipelines import pipeline

from utils.util import get_local_time_str
from steps.tf_train import train_tf_model, InputParams

@pipeline
def android_ml_pipeline(step_1):
    step_1()

tflite_pipeline_instance = android_ml_pipeline(
    step_1 = train_tf_model(InputParams(
        tf_version="2.11.0", # used to assert the tensorflow version required for this pipeline
        num_epochs=100, #100 num_epochs
        batch_size=100, #100 batch_size
        show_logs=False # deactivate debug logs, and plotting for none interactive mode
    ))
)

# https://docs.zenml.io/starter-guide/pipelines
my_run_name=f"my_custom_tflite_fashion_{get_local_time_str(target_tz_str='Europe/Berlin')}" 
tflite_pipeline_instance.run(run_name=my_run_name, unlisted=True, enable_cache=False)