# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""Filters can remove subscriptions after they are collected.
"""
import re

from trac.core import *
from trac.config import ListOption
from trac.perm import PermissionCache

from announcer.api import IAnnouncementSubscriptionFilter
from announcer.api import _

class DefaultPermissionFilter(Component):
    """DefaultPermissionFilter simply checks that each subscription
    has ${REALM}_VIEW permissions before allow the subscription notice
    to be sent.
    """
    implements(IAnnouncementSubscriptionFilter)

    exception_realms = ListOption('announcer', 'filter_exception_realms', '',
            """The PermissionFilter will filter an announcements for with the
            user doesn't have ${REALM}_VIEW permission.  If there is some
            realm that doesn't use a permission called ${REALM}_VIEW then
            you should add it to this list and create a custom filter to
            enforce it's permissions.  Be careful because permissions can be
            bypassed using the AnnouncerPlugin.
            """)

    def filter_subscriptions(self, event, subscriptions):
        action = '%s_VIEW'%event.realm.upper()
        for subscription in subscriptions:
            sid, auth = subscription[1:3]
            # PermissionCache already takes care of sid = None
            if not auth:
                sid = 'anonymous'
            perm = PermissionCache(self.env, sid)
            if perm.has_permission(action):
                yield subscription
            else:
                self.log.debug(
                    "Filtering %s because of rule: DefaultPermissionFilter"\
                    %sid
                )
