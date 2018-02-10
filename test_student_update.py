import logging
import sys
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

logging.debug('debug')
logging.info('info')
logging.error('error')
logging.critical('critical')