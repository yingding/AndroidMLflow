import os
from typing import Type
from zenml.io import fileio
from zenml.enums import ArtifactType
from zenml.materializers.base_materializer import BaseMaterializer
from utils.custom_model import Model

# https://docs.zenml.io/advanced-guide/pipelines/materializers
class ModelWrapperMaterializer(BaseMaterializer):
    ASSOCIATED_TYPES = (Model, )
    # ASSOCIATED_ARTIFACT_TYPE = ArtifactType.DATA
    ASSOCIATED_ARTIFACT_TYPE = ArtifactType.MODEL

    def load(self, data_type: Type[Model]) -> Model:
        """Read from artifact store"""
        super().load(data_type)
        
        path = os.path.join(self.uri, 'model.ckpt')
        with fileio.open(path, 'r') as f:
            # not using the opened file
            m = Model()
            m.restore(path) # instead of f
        return m 
    
    def save(self, my_obj: Model) -> None:
        """Write to artifact store"""
        super().save(my_obj)
        path = os.path.join(self.uri, 'model.ckpt')
        with fileio.open(path, 'w') as f:
            # not using the opend file but the path only
            my_obj.save(path)
