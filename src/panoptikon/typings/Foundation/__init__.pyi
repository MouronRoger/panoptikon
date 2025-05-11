"""Type stubs for Foundation framework."""

from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union

# Geometry functions
def NSMakeRect(x: float, y: float, width: float, height: float) -> Any: ...


def NSMakePoint(x: float, y: float) -> Any: ...


def NSMakeSize(width: float, height: float) -> Any: ...


# Commonly used constants
NSNotFound: int


# FS Constants
# FSEvents flags
kFSEventStreamCreateFlagNone: int
kFSEventStreamCreateFlagUseCFTypes: int
kFSEventStreamCreateFlagNoDefer: int
kFSEventStreamCreateFlagWatchRoot: int
kFSEventStreamCreateFlagIgnoreSelf: int
kFSEventStreamCreateFlagFileEvents: int

# FSEvents event types
kFSEventStreamEventFlagNone: int
kFSEventStreamEventFlagMustScanSubDirs: int
kFSEventStreamEventFlagUserDropped: int
kFSEventStreamEventFlagKernelDropped: int
kFSEventStreamEventFlagEventIdsWrapped: int
kFSEventStreamEventFlagHistoryDone: int
kFSEventStreamEventFlagRootChanged: int
kFSEventStreamEventFlagMount: int
kFSEventStreamEventFlagUnmount: int
kFSEventStreamEventFlagItemCreated: int
kFSEventStreamEventFlagItemRemoved: int
kFSEventStreamEventFlagItemInodeMetaMod: int
kFSEventStreamEventFlagItemRenamed: int
kFSEventStreamEventFlagItemModified: int
kFSEventStreamEventFlagItemFinderInfoMod: int
kFSEventStreamEventFlagItemChangeOwner: int
kFSEventStreamEventFlagItemXattrMod: int
kFSEventStreamEventFlagItemIsFile: int
kFSEventStreamEventFlagItemIsDir: int
kFSEventStreamEventFlagItemIsSymlink: int
kFSEventStreamEventFlagOwnEvent: int
kFSEventStreamEventFlagItemIsHardlink: int
kFSEventStreamEventFlagItemIsLastHardlink: int


class NSObject:
    """Base class for all Objective-C objects."""
    
    def init(self) -> "NSObject": ...
    
    def description(self) -> str: ...
    
    def className(self) -> str: ...
    
    def isEqual_(self, object: Any) -> bool: ...


class NSString:
    """Foundation string class."""
    
    @classmethod
    def stringWithString_(cls, string: str) -> "NSString": ...
    
    def length(self) -> int: ...
    
    def UTF8String(self) -> bytes: ...
    
    def characterAtIndex_(self, index: int) -> str: ...


class NSArray:
    """Foundation array class."""
    
    @classmethod
    def array(cls) -> "NSArray": ...
    
    @classmethod
    def arrayWithObjects_count_(cls, objects: Tuple[Any, ...], count: int) -> "NSArray": ...
    
    @classmethod
    def arrayWithObject_(cls, object: Any) -> "NSArray": ...
    
    def count(self) -> int: ...
    
    def objectAtIndex_(self, index: int) -> Any: ...
    
    def containsObject_(self, object: Any) -> bool: ...


class NSDictionary:
    """Foundation dictionary class."""
    
    @classmethod
    def dictionary(cls) -> "NSDictionary": ...
    
    @classmethod
    def dictionaryWithObjects_forKeys_count_(
        cls, objects: Tuple[Any, ...], keys: Tuple[Any, ...], count: int
    ) -> "NSDictionary": ...
    
    @classmethod
    def dictionaryWithObject_forKey_(cls, object: Any, key: Any) -> "NSDictionary": ...
    
    def count(self) -> int: ...
    
    def objectForKey_(self, key: Any) -> Any: ...
    
    def allKeys(self) -> NSArray: ...
    
    def allValues(self) -> NSArray: ...


class NSDate:
    """Date representation class."""
    
    @classmethod
    def date(cls) -> "NSDate": ...
    
    @classmethod
    def dateWithTimeIntervalSinceNow_(cls, seconds: float) -> "NSDate": ...
    
    @classmethod
    def dateWithTimeIntervalSince1970_(cls, seconds: float) -> "NSDate": ...
    
    def timeIntervalSince1970(self) -> float: ...
    
    def timeIntervalSinceDate_(self, date: "NSDate") -> float: ...


class NSURL:
    """URL handling class."""
    
    @classmethod
    def URLWithString_(cls, string: str) -> "NSURL": ...
    
    @classmethod
    def fileURLWithPath_(cls, path: str) -> "NSURL": ...
    
    @classmethod
    def fileURLWithPath_isDirectory_(cls, path: str, isDirectory: bool) -> "NSURL": ...
    
    def path(self) -> str: ...
    
    def absoluteString(self) -> str: ...
    
    def isFileURL(self) -> bool: ...


class NSNotification:
    """Notification object for the notification center system."""
    
    @classmethod
    def notificationWithName_object_(cls, name: str, object: Any) -> "NSNotification": ...
    
    @classmethod
    def notificationWithName_object_userInfo_(
        cls, name: str, object: Any, userInfo: NSDictionary
    ) -> "NSNotification": ...
    
    def name(self) -> str: ...
    
    def object(self) -> Any: ...
    
    def userInfo(self) -> NSDictionary: ...


class NSNotificationCenter:
    """Central notification dispatch service."""
    
    @classmethod
    def defaultCenter(cls) -> "NSNotificationCenter": ...
    
    def addObserver_selector_name_object_(
        self, observer: Any, selector: str, name: str, object: Any
    ) -> None: ...
    
    def removeObserver_(self, observer: Any) -> None: ...
    
    def removeObserver_name_object_(
        self, observer: Any, name: str, object: Any
    ) -> None: ...
    
    def postNotification_(self, notification: NSNotification) -> None: ...
    
    def postNotificationName_object_(self, name: str, object: Any) -> None: ...
    
    def postNotificationName_object_userInfo_(
        self, name: str, object: Any, userInfo: Dict[Any, Any]
    ) -> None: ...


# FSEvents (File System Events) related classes
class FSEventStreamRef:
    """Opaque reference to a file system events stream."""
    
    pass


# FSEvents functions
def FSEventStreamCreate(
    allocator: Any,
    callback: Callable[..., None], 
    context: Any,
    pathsToWatch: List[str],
    sinceWhen: Any,
    latency: float,
    flags: int
) -> FSEventStreamRef: ...


def FSEventStreamScheduleWithRunLoop(
    stream: FSEventStreamRef, 
    runLoop: Any, 
    runLoopMode: str
) -> None: ...


def FSEventStreamStart(stream: FSEventStreamRef) -> bool: ...


def FSEventStreamStop(stream: FSEventStreamRef) -> None: ...


def FSEventStreamInvalidate(stream: FSEventStreamRef) -> None: ...


def FSEventStreamRelease(stream: FSEventStreamRef) -> None: ...


def FSEventStreamGetLatestEventId(stream: FSEventStreamRef) -> int: ...


def FSEventStreamFlushAsync(stream: FSEventStreamRef) -> int: ...


def FSEventStreamFlushSync(stream: FSEventStreamRef) -> None: ...


def FSEventStreamShow(stream: FSEventStreamRef) -> None: ...


def FSEventsCopyPath(stream: FSEventStreamRef, index: int) -> str: ... 