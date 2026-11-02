/*
 */

#include <stdlib.h>
#include <stdint.h>
#include "wayland-util.h"

extern const struct wl_interface ivi_hmi_client_interface;
extern const struct wl_interface ivi_hmi_receiver_interface;
extern const struct wl_interface ivi_info_receiver_interface;

static const struct wl_interface *types[] = {
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	&ivi_hmi_client_interface,
	NULL,
	&ivi_hmi_receiver_interface,
	NULL,
	NULL,
	&ivi_hmi_receiver_interface,
	&ivi_info_receiver_interface,
};

static const struct wl_message ivi_window_manager_requests[] = {
	{ "update_layout", "u", types + 0 },
	{ "get_primary_screen_size", "", types + 0 },
	{ "set_surface_visible", "uu", types + 0 },
	{ "request_fg", "iu", types + 0 },
	{ "show_notification", "iu", types + 0 },
	{ "show_PAS", "iu", types + 0 },
	{ "set_surface_layout", "uiiii", types + 0 },
	{ "set_surface_alpha", "ui", types + 0 },
	{ "set_visible_for_qtwayland", "ui", types + 0 },
	{ "expand_drawer", "ii", types + 0 },
	{ "set_surface_to_top_order_within_layer", "u", types + 0 },
	{ "set_parent_child_surface", "uu", types + 0 },
	{ "set_surface_to_full_screen", "uiu", types + 0 },
	{ "request_fg_with_app_id", "is", types + 0 },
	{ "set_surface_to_full_screen_with_app_id", "isiu", types + 0 },
	{ "set_app_name_with_app_type", "us", types + 0 },
	{ "show_app_with_app_type", "iuu", types + 0 },
	{ "set_surface_position_with_app_id", "isii", types + 0 },
	{ "request_clone_surface_create", "uuuiiii", types + 0 },
	{ "set_clone_surface_layout", "uiiii", types + 0 },
	{ "request_clone_surface_destroy", "u", types + 0 },
	{ "request_move_layer", "iiii", types + 0 },
};

static const struct wl_message ivi_window_manager_events[] = {
	{ "primary_screen_size", "uu", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_window_manager_interface = {
	"ivi_window_manager", 1,
	22, ivi_window_manager_requests,
	1, ivi_window_manager_events,
};

static const struct wl_message ivi_hmi_receiver_requests[] = {
	{ "destroy", "", types + 0 },
};

static const struct wl_message ivi_hmi_receiver_events[] = {
	{ "receive_id", "u", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_hmi_receiver_interface = {
	"ivi_hmi_receiver", 1,
	1, ivi_hmi_receiver_requests,
	1, ivi_hmi_receiver_events,
};

static const struct wl_message ivi_hmi_requester_requests[] = {
	{ "destroy", "", types + 0 },
	{ "create_hmi_client", "iu?sn", types + 7 },
	{ "request_id", "?sn", types + 11 },
	{ "reserve_id", "uun", types + 13 },
};

WL_EXPORT const struct wl_interface ivi_hmi_requester_interface = {
	"ivi_hmi_requester", 1,
	4, ivi_hmi_requester_requests,
	0, NULL,
};

static const struct wl_message ivi_hmi_client_requests[] = {
	{ "destroy", "", types + 0 },
	{ "set_app_id", "?s", types + 0 },
	{ "set_display_plane", "i", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_hmi_client_interface = {
	"ivi_hmi_client", 1,
	3, ivi_hmi_client_requests,
	0, NULL,
};

static const struct wl_message ivi_info_receiver_requests[] = {
	{ "destroy", "", types + 0 },
};

static const struct wl_message ivi_info_receiver_events[] = {
	{ "receive_BG_info", "ui?s", types + 0 },
	{ "receive_FG_info", "ui?s", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_info_receiver_interface = {
	"ivi_info_receiver", 1,
	1, ivi_info_receiver_requests,
	2, ivi_info_receiver_events,
};

static const struct wl_message ivi_info_requester_requests[] = {
	{ "destroy", "", types + 0 },
	{ "create_info_receiver", "n", types + 16 },
};

WL_EXPORT const struct wl_interface ivi_info_requester_interface = {
	"ivi_info_requester", 1,
	2, ivi_info_requester_requests,
	0, NULL,
};

