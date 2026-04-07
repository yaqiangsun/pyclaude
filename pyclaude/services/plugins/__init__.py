"""Plugins service.

Provides plugin management functionality including:
- Plugin installation, uninstallation, enable/disable, update
- Marketplace management
- Plugin loading and caching
- Settings management
"""

from .installed_plugins_manager import (
    add_installed_plugin,
    get_plugin_installation_for_scope,
    get_plugin_installations,
    is_plugin_installed,
    load_installed_plugins_from_disk,
    remove_plugin_installation,
    save_installed_plugins_to_disk,
    update_installation_path_on_disk,
)

from .marketplace_manager import (
    add_marketplace_source,
    get_marketplace,
    get_marketplace_cache_only,
    get_plugin_by_id,
    get_plugin_by_id_cache_only,
    load_known_marketplaces_config,
    refresh_all_marketplaces,
    refresh_marketplace,
    remove_marketplace_source,
    save_known_marketplaces_config,
    search_plugin_in_marketplaces,
)

from .plugin_directories import (
    ensure_plugin_dirs,
    get_marketplaces_cache_dir,
    get_plugin_cache_dir,
    get_plugin_data_dir,
    get_plugin_seed_dirs,
    get_plugins_directory,
    get_versioned_cache_path,
    get_versioned_zip_cache_path,
)

from .plugin_identifier import (
    build_plugin_id,
    is_official_marketplace_name,
    parse_plugin_identifier,
    scope_to_setting_source,
    setting_source_to_scope,
)

from .plugin_loader import (
    cache_plugin,
    calculate_plugin_version,
    get_git_commit_sha,
    load_plugin_manifest,
)

from .plugin_operations import (
    PluginOperationResult,
    PluginUpdateResult,
    VALID_INSTALLABLE_SCOPES,
    VALID_UPDATE_SCOPES,
    disable_all_plugins_op,
    disable_plugin_op,
    enable_plugin_op,
    install_plugin_op,
    set_plugin_enabled_op,
    uninstall_plugin_op,
    update_plugin_op,
)

from .schemas import (
    ALLOWED_OFFICIAL_MARKETPLACE_NAMES,
    CommandMetadata,
    DependencyRef,
    HooksConfig,
    InstalledPluginsData,
    KnownMarketplace,
    KnownMarketplacesFile,
    LspServerConfig,
    McpServerConfig,
    MarketplaceSource,
    MarketplaceSourceDirectory,
    MarketplaceSourceFile,
    MarketplaceSourceGithub,
    MarketplaceSourceGit,
    MarketplaceSourceNpm,
    MarketplaceSourceSettings,
    MarketplaceSourceUrl,
    PluginAuthor,
    PluginInstallation,
    PluginManifest,
    PluginScope,
    PluginSource,
    PluginSourceDirectory,
    PluginSourceFile,
    PluginSourceGit,
    PluginSourceNpm,
    PluginMarketplaceEntry,
    is_blocked_official_name,
    is_marketplace_auto_update,
    validate_marketplace_name,
    validate_official_name_source,
    validate_plugin_name,
)

__all__ = [
    # installed_plugins_manager
    'add_installed_plugin',
    'get_plugin_installation_for_scope',
    'get_plugin_installations',
    'is_plugin_installed',
    'load_installed_plugins_from_disk',
    'remove_plugin_installation',
    'save_installed_plugins_to_disk',
    'update_installation_path_on_disk',
    # marketplace_manager
    'add_marketplace_source',
    'get_marketplace',
    'get_marketplace_cache_only',
    'get_plugin_by_id',
    'get_plugin_by_id_cache_only',
    'load_known_marketplaces_config',
    'refresh_all_marketplaces',
    'refresh_marketplace',
    'remove_marketplace_source',
    'save_known_marketplaces_config',
    'search_plugin_in_marketplaces',
    # plugin_directories
    'ensure_plugin_dirs',
    'get_marketplaces_cache_dir',
    'get_plugin_cache_dir',
    'get_plugin_data_dir',
    'get_plugin_seed_dirs',
    'get_plugins_directory',
    'get_versioned_cache_path',
    'get_versioned_zip_cache_path',
    # plugin_identifier
    'build_plugin_id',
    'is_official_marketplace_name',
    'parse_plugin_identifier',
    'scope_to_setting_source',
    'setting_source_to_scope',
    # plugin_loader
    'cache_plugin',
    'calculate_plugin_version',
    'get_git_commit_sha',
    'load_plugin_manifest',
    # plugin_operations
    'PluginOperationResult',
    'PluginUpdateResult',
    'VALID_INSTALLABLE_SCOPES',
    'VALID_UPDATE_SCOPES',
    'disable_all_plugins_op',
    'disable_plugin_op',
    'enable_plugin_op',
    'install_plugin_op',
    'set_plugin_enabled_op',
    'uninstall_plugin_op',
    'update_plugin_op',
    # schemas
    'ALLOWED_OFFICIAL_MARKETPLACE_NAMES',
    'CommandMetadata',
    'DependencyRef',
    'HooksConfig',
    'InstalledPluginsData',
    'KnownMarketplace',
    'KnownMarketplacesFile',
    'LspServerConfig',
    'McpServerConfig',
    'MarketplaceSource',
    'MarketplaceSourceDirectory',
    'MarketplaceSourceFile',
    'MarketplaceSourceGithub',
    'MarketplaceSourceGit',
    'MarketplaceSourceNpm',
    'MarketplaceSourceSettings',
    'MarketplaceSourceUrl',
    'PluginAuthor',
    'PluginInstallation',
    'PluginManifest',
    'PluginScope',
    'PluginSource',
    'PluginSourceDirectory',
    'PluginSourceFile',
    'PluginSourceGit',
    'PluginSourceNpm',
    'PluginMarketplaceEntry',
    'is_blocked_official_name',
    'is_marketplace_auto_update',
    'validate_marketplace_name',
    'validate_official_name_source',
    'validate_plugin_name',
]