import datetime
from dateutil import relativedelta
dateFrom = datetime.datetime.now() - relativedelta.relativedelta(months=6) 
dateFrom = dateFrom.strftime('%Y-%m-%d')

search_url = "http://www.esma.europa.eu/databases-library/esma-library?f[0]=im_field_document_type%3A41&date_from="+dateFrom+"&date_to=%2A"
