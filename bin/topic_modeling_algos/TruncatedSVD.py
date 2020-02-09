'''
Based on Template from 
https://docs.splunk.com/Documentation/MLApp/latest/API/Writeanalgorithmclass#BaseAlgo_class
and using existing Splunk PCA implementation as it is the most similar algorithim
'''

from sklearn.decomposition import TruncatedSVD as _TruncatedSVD
from base import BaseAlgo, TransformerMixin
from codec import codecs_manager
from util.param_util import convert_params
from six.moves import range

class TruncatedSVD(TransformerMixin, BaseAlgo):

    def __init__(self, options):
        self.handle_options(options)
        out_params = convert_params(
            options.get('params', {}),
            ints=['k'],
            aliases={'k': 'n_components'}
        )

        self.estimator = _TruncatedSVD(**out_params)

    def rename_output(self, default_names, new_names):
        if new_names is None:
            new_names = 'SVD'
        output_names = ['{}_{}'.format(new_names, i+1) for i in range(len(default_names))]
        return output_names

    @staticmethod
    def register_codecs():
        from codec.codecs import SimpleObjectCodec
        codecs_manager.add_codec('topic_modeling_algos.TruncatedSVD', 'TruncatedSVD', SimpleObjectCodec)
        codecs_manager.add_codec('sklearn.decomposition.truncated_svd', 'TruncatedSVD', SimpleObjectCodec)
