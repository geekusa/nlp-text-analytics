from sklearn.decomposition import TruncatedSVD as _TruncatedSVD
from base import BaseAlgo, TransformerMixin
from codec import codecs_manager
from util.param_util import convert_params

'''
Based on Template from 
https://docs.splunk.com/Documentation/MLApp/latest/API/Writeanalgorithmclass#BaseAlgo_class
and using existing Splunk PCA implementation as it is the most similar algorithim

class CustomAlgoTemplate(BaseAlgo):
    def __init__(self, options):
        # Option checking & initializations here
        pass

    def fit(self, df, options):
        # Fit an estimator to df, a pandas DataFrame of the search results
        pass

    def partial_fit(self, df, options):
        # Incrementally fit a model
        pass

    def apply(self, df, options):
        # Apply a saved model
        # Modify df, a pandas DataFrame of the search results
        return df

    @staticmethod
    def register_codecs():
        # Add codecs to the codec manager
        pass
'''



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
        output_names = ['{}_{}'.format(new_names, i+1) for i in xrange(len(default_names))]
        return output_names

    @staticmethod
    def register_codecs():
        from codec.codecs import SimpleObjectCodec
        codecs_manager.add_codec('algos.TruncatedSVD', 'TruncatedSVD', SimpleObjectCodec)
        codecs_manager.add_codec('sklearn.decomposition.truncatedsvd', 'TruncatedSVD', SimpleObjectCodec)
