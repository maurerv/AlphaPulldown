""" Implements structure prediction backend using OpenFold.

    Copyright (c) 2024 European Molecular Biology Laboratory

    Author: Dingquan Yu <dingquan.yu@embl-hamburg.de>
"""
from typing import Dict
from alphapulldown.objects import MultimericObject
from alphapulldown.folding_backend import FoldingBackend
from absl import logging
logging.set_verbosity(logging.INFO)

class OpenfoldBackend(FoldingBackend):
    """
    A backend class for running protein structure predictions using the OpenFold model.
    """
    @staticmethod
    def setup(
        model_name: str,
        model_dir: str,
        output_dir: str,
        multimeric_object: MultimericObject,
        **kwargs,
    ) -> Dict:
        """
        Initializes and configures a UniFold model runner.

        Parameters
        ----------
        model_name : str
            The name of the model to use for prediction.
        model_dir : str
            The directory where the model files are located.
        output_dir : str
            The directory where the prediction outputs will be saved.
        multimeric_object : MultimericObject
            An object containing the description and features of the
            multimeric protein to predict.
        **kwargs : dict
            Additional keyword arguments for model configuration.

        Returns
        -------
        Dict
            A dictionary containing the model runner, arguments, and configuration.
        """
        from openfold.run_pretrained_openfold import create_general_args, create_model_config

        from torch import cuda
        try:
            device_id = cuda.current_device()
            device = f"cuda:{device_id}"
        except:
            device = f"cpu"
            logging.warning(
                "Failed to detect any CUDA device. Now running predictions on CPU, which can be really slow")
        openfold_checkpoint_path = kwargs.get("openfold_checkpoint_path", None)
        jax_param_path = kwargs.get("jax_param_path", None)
        general_args = create_general_args(config_preset=model_name, model_device=device,
                                           jax_param_path=jax_param_path, openfold_checkpoint_path=openfold_checkpoint_path,
                                           output_dir=output_dir, trace_model=False,
                                           subtract_plddt=False, multimer_ri_gap=200,
                                           save_outputs=True, skip_relaxation=False
                                           )

        configs = create_model_config(general_args)
        return {
            "model_args": general_args,
            "model_config": configs,
        }

    def predict(
        self,
        model_runner,
        model_args,
        model_config: Dict,
        multimeric_object: MultimericObject,
        random_seed: int = 42,
        **kwargs,
    ) -> None:
        """
        Predicts the structure of proteins using configured UniFold models.

        Parameters
        ----------
        model_runner
            The configured model runner for predictions obtained
            from :py:meth:`UnifoldBackend.setup`.
        model_args
            Arguments used for running the UniFold prediction obtained from
            from :py:meth:`UnifoldBackend.setup`.
        model_config : Dict
            Configuration dictionary for the UniFold model obtained from
            from :py:meth:`UnifoldBackend.setup`.
        multimeric_object : MultimericObject
            An object containing the features of the multimeric protein to predict.
        random_seed : int, optional
            The random seed for prediction reproducibility, default is 42.
        **kwargs : dict
            Additional keyword arguments for prediction.
        """
        from openfold.run_pretrained_openfold import preprocess_feature_dict as openfold_preprocess_feature_dict
        from openfold.run_pretrained_openfold import open_fold_predict, create_model_generator
        preprocessed_features, feature_processor = openfold_preprocess_feature_dict(
            multimeric_object.feature_dict)
        model_generators = create_model_generator(model_config, model_args)
        logging.info(f"Now running structural prediction on {multimeric_object.description} using OpenFold models.")
        open_fold_predict(model_generator=model_generators, processed_feature_dict=preprocessed_features,
                          args=model_args, tag=multimeric_object.description,
                          feature_dict=multimeric_object.feature_dict, 
                          feature_processor=feature_processor,
                          config=model_config, output_name=multimeric_object.description)

        return None

    def postprocess(**kwargs) -> None:
        return None
