"""
Bridge module - Remote control/session management.
"""

from .bridge_main import BridgeMain, BridgeConfig
from .repl_bridge import REPLBridge, REPLBridgeConfig
from .session import Session, SessionManager
from .types import BridgeMessage, BridgeEvent, BridgeState, BridgeConfig as BridgeConfigType
from .bridge_config import get_bridge_config, set_bridge_config, get_bridge_url
from .bridge_enabled import is_bridge_enabled, set_bridge_enabled
from .bridge_debug import bridge_debug, get_debugger
from .poll_config import PollConfig, get_poll_config, update_poll_config
from .jwt_utils import create_jwt_token, decode_jwt_token, is_jwt_expired
from .inbound_messages import InboundMessageHandler, get_inbound_handler
from .inbound_attachments import InboundAttachmentsHandler, get_attachments_handler
from .create_session import create_session, CreateSessionParams
from .code_session_api import CodeSessionAPI, create_code_session_api
from .remote_bridge_core import RemoteBridgeCore
from .session_id_compat import normalize_session_id, format_session_id, is_valid_session_id
from .env_less_bridge_config import EnvLessBridgeConfig, get_env_less_bridge_config
from .flush_gate import FlushGate, get_flush_gate, FlushMode
from .capacity_wake import CapacityWake, get_capacity_wake
from .bridge_ui import BridgeUIState, get_default_ui_state, format_bridge_status
from .bridge_pointer import BridgePointer, create_forward_pointer, create_backward_pointer
from .bridge_status_util import BridgeStatusLevel, get_bridge_status_info
from .bridge_permission_callbacks import PermissionType, PermissionResult, request_permission
from .repl_bridge_transport import ReplBridgeTransport
from .trusted_device import get_device_id, is_device_trusted, trust_device, untrust_device
from .work_secret import generate_work_secret, set_work_secret, get_work_secret, validate_work_secret

__all__ = [
    'BridgeMain',
    'BridgeConfig',
    'REPLBridge',
    'REPLBridgeConfig',
    'Session',
    'SessionManager',
    'BridgeMessage',
    'BridgeEvent',
    'BridgeState',
    'BridgeConfigType',
    'get_bridge_config',
    'set_bridge_config',
    'get_bridge_url',
    'is_bridge_enabled',
    'set_bridge_enabled',
    'bridge_debug',
    'get_debugger',
    'PollConfig',
    'get_poll_config',
    'update_poll_config',
    'create_jwt_token',
    'decode_jwt_token',
    'is_jwt_expired',
    'InboundMessageHandler',
    'get_inbound_handler',
    'InboundAttachmentsHandler',
    'get_attachments_handler',
    'create_session',
    'CreateSessionParams',
    'CodeSessionAPI',
    'create_code_session_api',
    'RemoteBridgeCore',
    'normalize_session_id',
    'format_session_id',
    'is_valid_session_id',
    'EnvLessBridgeConfig',
    'get_env_less_bridge_config',
    'FlushGate',
    'get_flush_gate',
    'FlushMode',
    'CapacityWake',
    'get_capacity_wake',
    'BridgeUIState',
    'get_default_ui_state',
    'format_bridge_status',
    'BridgePointer',
    'create_forward_pointer',
    'create_backward_pointer',
    'BridgeStatusLevel',
    'get_bridge_status_info',
    'PermissionType',
    'PermissionResult',
    'request_permission',
    'ReplBridgeTransport',
    'get_device_id',
    'is_device_trusted',
    'trust_device',
    'untrust_device',
    'generate_work_secret',
    'set_work_secret',
    'get_work_secret',
    'validate_work_secret',
]