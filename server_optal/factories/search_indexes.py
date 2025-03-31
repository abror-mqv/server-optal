from haystack import indexes
from .models import Product
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import TEXT

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name")
    description = indexes.CharField(model_attr="description", null=True)
    text_analyzer = StemmingAnalyzer("russian")    
    def get_model(self):
        return Product
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
