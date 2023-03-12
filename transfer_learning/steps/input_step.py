from zenml.steps import step, BaseParameters

class InputParams(BaseParameters):
    """Input Params for pipeline"""
    tf_version: str = ""
    num_epochs: int = 100
    batch_size: int = 100
    show_logs: bool = False


@step
def input_step(
    params: InputParams
) -> InputParams:
    return params     