from zenml.steps import step
from steps.input_step import InputParams
from steps.model_wrapper_materializer import ModelWrapperMaterializer

# from tensorflow.keras import Model as TF_Model

# Model wrapper
from utils.custom_model import Model as CustomModel 
  
@step(output_materializers=ModelWrapperMaterializer)
def train_tf_model(params: InputParams) -> CustomModel:
    '''
    This model trains a fashion mnist model, and convert to tensorflow lite mode with the following exposed functions
    * train
    * infer
    * save
    * restore
    functions
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    import tensorflow as tf
    from utils.custom_model import Model, IMG_SIZE
    from utils.helper import (
        create_default_tf_checkpoint_subfolder, 
        create_default_data_exchange_path,
        PreviousTrainingResults,
        SerializableList
    )
    from utils.visual import (
        display_training_loss,
        PlotLineData
    )
    from utils.util import log as tag_log
    def log(msg: str):
        tag_log(
            is_logging=params.show_logs,
            tag="tf_training",
            msg=msg
        )

    log(f"Tensorflow verion: {tf.version.VERSION}")

    # quick version check for this code
    assert tf.version.VERSION == params.tf_version # "2.11.0"


    fashion_mnist = tf.keras.datasets.fashion_mnist
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

    ###
    # Preprocess the data
    # Pixel values in this dataset are between 0 and 255, and must be normalized to a value
    # between 0 and 1 for processing by the model. Divide the values by 255 to make this adustment
    ###
    train_images = (train_images / 255.0).astype(np.float32)
    test_images = (test_images / 255.0).astype(np.float32)

    ## Convert the data labels to categorical values by performing one-hot encoding
    train_labels = tf.keras.utils.to_categorical(train_labels)
    test_labels = tf.keras.utils.to_categorical(test_labels)

    NUM_EPOCHS = params.num_epochs #100
    BATCH_SIZE = params.batch_size #100

    epochs = np.arange(1, NUM_EPOCHS + 1, 1)
    losses = np.zeros([NUM_EPOCHS])
    m = Model()

    train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels))
    train_ds = train_ds.batch(BATCH_SIZE)

    for i in range(NUM_EPOCHS):
        for x, y in train_ds:
            result = m.train(x, y)

        losses[i] = result['loss'] 
        if (i + 1) % 10 == 0:
            print(f"Finished {i+1} epochs")
            print(f"   loss: {losses[i]:.3f}")
    
    log("""saving model checkpoint""")
    # Save the trained weights to a checkpoint, 
    current_model_path = create_default_tf_checkpoint_subfolder()
    if current_model_path is not None:
        m.save(f"{current_model_path}/model.ckpt")
    
    log("""saving model performance log""")
    # Save epochs and losses for later use
    data_exchange_path = create_default_data_exchange_path(exchange_file_name="previous_training_results_dataclass")
    previous_training_results = PreviousTrainingResults(epochs=epochs, losses=losses)
    previous_training_results.dump(data_exchange_path)

    # save the original training set label as logits, the logits is a list of probabilities
    logits_tf_original_path = create_default_data_exchange_path(exchange_file_name="logits_tf_original")
    logits_original = SerializableList(m.infer(x=train_images[:1])['logits'][0])
    logits_original.dump(logits_tf_original_path)

    ###
    # Plot the training result, only in debug enabled mode
    ###
    display_training_loss(
        lines=[PlotLineData(
            x_values=previous_training_results.epochs, 
            y_values=previous_training_results.losses, 
            label="Pre-training")
        ], 
        plt_func=plt.show,
        visiable=params.show_logs
    )

    """return the trained model"""
    return m