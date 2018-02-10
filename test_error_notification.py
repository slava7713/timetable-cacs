import logging
from raygun_notifier import client
log = logging.getLogger(__name__)
log.critical('No updates for %d people!' % 213123123123)

client.send_exception(userCustomData={'error_count': 213123123123})
