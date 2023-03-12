from zenml.pipelines import pipeline

from utils.util import get_local_time_str
from steps.tf_train import train_tf_model
from steps.tflite_convert import convert_tflite_model
from steps.input_step import input_step, InputParams

@pipeline
def android_ml_pipeline(step_1, step_2):
    # params = step_0()
    tf_model = step_1()
    step_2(tf_model)

# define the global pipeline params
pipeline_params = InputParams(
    tf_version="2.11.0", # used to assert the tensorflow version required for this pipeline
    num_epochs=100, #100 num_epochs
    batch_size=100, #100 batch_size
    show_logs=True #False # deactivate debug logs, and plotting for none interactive mode
)

# initialize a pipeline with the pipeline params
tflite_pipeline_instance = android_ml_pipeline(
    # step_0 = input_step(pipeline_params), # specify input param at runtime
    step_1 = train_tf_model(pipeline_params),
    step_2 = convert_tflite_model(pipeline_params)
)

# https://docs.zenml.io/starter-guide/pipelines
my_run_name=f"my_custom_tflite_fashion_{get_local_time_str(target_tz_str='Europe/Berlin')}" 
tflite_pipeline_instance.run(run_name=my_run_name, unlisted=True, enable_cache=False)