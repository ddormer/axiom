
from zope.interface import Interface, Attribute

class IStatEvent(Interface):
    """
    Marker for a log message that is useful as a statistic.

    Log messages with 'interface' set to this class will be counted over time.
    This is useful for tracking the rate of events such as page views. These
    messages are observed and thus tracked with a quotient.stats.Statoscope.
    These Statoscopes are periodically saved and are made retrievable by a
    remote interface.

    Log messages conforming to this interface must have these keys:

    - 'name': the name to be used for the backing Statoscope. This is used to
      group related stats for a component. Examples: "IMAP grabber",
      "database".

    Optional keys:

    - 'user': if this stat is something that can be blamed squarely on one
      user, set this to the username (avatar.name)

    - keys starting with 'stat_' map 'stuffs' to 'how many stuffs'. For
      example, stat_bytes=3182.

    """


class IAtomicFile(Interface):
    def __init__(tempname, destdir):
        """Create a new atomic file.

        The file will exist temporarily at C{tempname} and be relocated to
        C{destdir} when it is closed.
        """

    def tell():
        """Return the current offset into the file, in bytes.
        """

    def write(bytes):
        """Write some bytes to this file.
        """

    def close(callback):
        """Close this file.  Move it to its final location.

        @param callback: A no-argument callable which will be invoked
        when this file is ready to be moved to its final location.  It
        must return the segment of the path relative to per-user
        storage of the owner of this file.  Alternatively, a string
        with semantics the same as those previously described for the
        return value of the callable.

        @rtype: C{axiom.store.StoreRelativePath}
        @return: A Deferred which fires with the full path to the file
        when it has been closed, or which fails if there is some error
        closing the file.
        """

    def abort():
        """Give up on this file.  Discard its contents.
        """


class IAxiomaticCommand(Interface):
    """
    Subcommand for 'axiomatic' and 'tell-axiom' command line programs.

    Should subclass twisted.python.usage.Options and provide a command to run.

    '.parent' attribute will be set to an object with a getStore method.
    """

    name = Attribute("""
    """)

    description = Attribute("""
    """)



class IBeneficiary(Interface):
    """
    Interface to adapt to when looking for an appropriate application-level
    object to install powerups on.
    """

    def powerUp(implementor, interface):
        """ Install a powerup on this object.  There is not necessarily any inverse
        powerupsFor on a beneficiary, although there may be; installations may
        be forwarded to a different implementation object, or deferred.
        """

class IScheduler(Interface):
    """
    An interface for scheduling tasks.  Quite often the store will be adaptable
    to this; in any Mantissa application, for example; so it is reasonable to
    assume that it is if your application needs to schedule timed events or
    queue tasks.
    """
    def schedule(self, runnable, when):
        """
        @param runnable: any Item with a 'run' method.

        @param when: a Time instance describing when the runnable's run()
        method will be called.  See extime.Time's documentation for more
        details.
        """

class IComparison(Interface):
    """
    An object that represents an in-database comparison.  A predicate that may
    apply to certain items in a store.  Passed as an argument to
    attributes.AND, .OR, and Store.query(...)
    """

class IOrdering(Interface):
    """
    An object suitable for passing to the 'sort' argument of a query method.
    """


class IReliableListener(Interface):
    """
    Receives notification of the existence of Items of a particular type.

    {IReliableListener} providers are given to
    L{IBatchProcessor.addReliableListener} and will then have L{processItem}
    called with items handled by that processor.
    """

    def processItem(item):
        """
        Callback notifying this listener of the existence of the given item.
        """

    def suspend():
        """
        Invoked when notification for this listener is being temporarily
        suspended.

        This should clean up any ephemeral resources held by this listener and
        generally prepare to not do anything for a while.
        """

    def resume():
        """
        Invoked when notification for this listener is being resumed.

        Any actions taken by L{suspend} may be reversed by this method.
        """


LOCAL, REMOTE = range(2)
class IBatchProcessor(Interface):
    def addReliableListener(listener, style=LOCAL):
        """
        Add the given Item to the set which will be notified of Items
        available for processing.

        Note: Each Item is processed synchronously.  Adding too many
        listeners to a single batch processor will cause the L{step}
        method to block while it sends notification to each listener.

        @type listener: L{IReliableListener}
        @param listener: The item to which listened-for items will be passed
        for processing.
        """


    def removeReliableListener(listener):
        """
        Remove a previously added listener.
        """


    def getReliableListeners():
        """
        Return an iterable of the listeners which have been added to
        this batch processor.
        """


class IBatchService(Interface):
    """
    Object which allows minimal communication with L{IReliableListener}
    providers which are running remotely (that is, with the L{REMOTE} style).
    """

    def suspend(storeID):
        """
        @type storeID: C{int}
        @param storeID: The storeID of the listener to suspend.

        @rtype: L{twisted.internet.defer.Deferred}
        @return: A Deferred which fires when the listener has been suspended.
        """

    def resume(storeID):
        """
        @type storeID: C{int}
        @param storeID: The storeID of the listener to resume.

        @rtype: L{twisted.internet.defer.Deferred}
        @return: A Deferred which fires when the listener has been resumed.
        """
