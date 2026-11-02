/*
 * Interface definitions reconstructed from the vendor Gen5W build of
 * weston 1.10 (ivi-controller.so). The protocol itself is the GENIVI
 * IVI layer management controller interface (DENSO CORPORATION / BMW Car IT
 * GmbH, MIT).
 */

#include <stdlib.h>
#include <stdint.h>
#include "wayland-util.h"

extern const struct wl_interface ivi_controller_layer_interface;
extern const struct wl_interface ivi_controller_screen_interface;
extern const struct wl_interface ivi_controller_surface_interface;
extern const struct wl_interface ivi_share_surface_interface;

static const struct wl_interface *types[] = {
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	&ivi_controller_layer_interface,
	NULL,
	&ivi_controller_surface_interface,
	NULL,
	&ivi_controller_screen_interface,
	&ivi_controller_surface_interface,
	&ivi_controller_surface_interface,
	&ivi_controller_layer_interface,
	&ivi_controller_layer_interface,
	&ivi_share_surface_interface,
	NULL,
};

static const struct wl_message ivi_controller_requests[] = {
	{ "commit_changes", "", types + 0 },
	{ "layer_create", "uiin", types + 5 },
	{ "surface_create", "un", types + 9 },
};

static const struct wl_message ivi_controller_events[] = {
	{ "screen", "un", types + 11 },
	{ "layer", "u", types + 0 },
	{ "surface", "u", types + 0 },
	{ "error", "iii?s", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_controller_interface = {
	"ivi_controller", 1,
	3, ivi_controller_requests,
	4, ivi_controller_events,
};

static const struct wl_message ivi_controller_layer_requests[] = {
	{ "set_visibility", "u", types + 0 },
	{ "set_opacity", "f", types + 0 },
	{ "set_source_rectangle", "iiii", types + 0 },
	{ "set_destination_rectangle", "iiii", types + 0 },
	{ "set_configuration", "ii", types + 0 },
	{ "set_orientation", "i", types + 0 },
	{ "screenshot", "s", types + 0 },
	{ "clear_surfaces", "", types + 0 },
	{ "add_surface", "o", types + 13 },
	{ "remove_surface", "o", types + 14 },
	{ "set_render_order", "a", types + 0 },
	{ "destroy", "i", types + 0 },
};

static const struct wl_message ivi_controller_layer_events[] = {
	{ "visibility", "i", types + 0 },
	{ "opacity", "f", types + 0 },
	{ "source_rectangle", "iiii", types + 0 },
	{ "destination_rectangle", "iiii", types + 0 },
	{ "configuration", "ii", types + 0 },
	{ "orientation", "i", types + 0 },
	{ "screen", "?o", types + 0 },
	{ "destroyed", "", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_controller_layer_interface = {
	"ivi_controller_layer", 1,
	12, ivi_controller_layer_requests,
	8, ivi_controller_layer_events,
};

static const struct wl_message ivi_controller_surface_requests[] = {
	{ "set_visibility", "u", types + 0 },
	{ "set_opacity", "f", types + 0 },
	{ "set_source_rectangle", "iiii", types + 0 },
	{ "set_destination_rectangle", "iiii", types + 0 },
	{ "set_configuration", "ii", types + 0 },
	{ "set_orientation", "i", types + 0 },
	{ "screenshot", "s", types + 0 },
	{ "send_stats", "", types + 0 },
	{ "destroy", "i", types + 0 },
};

static const struct wl_message ivi_controller_surface_events[] = {
	{ "visibility", "i", types + 0 },
	{ "opacity", "f", types + 0 },
	{ "source_rectangle", "iiii", types + 0 },
	{ "destination_rectangle", "iiii", types + 0 },
	{ "configuration", "ii", types + 0 },
	{ "orientation", "i", types + 0 },
	{ "pixelformat", "i", types + 0 },
	{ "layer", "?o", types + 15 },
	{ "stats", "uuuu?s", types + 0 },
	{ "destroyed", "", types + 0 },
	{ "content", "i", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_controller_surface_interface = {
	"ivi_controller_surface", 1,
	9, ivi_controller_surface_requests,
	11, ivi_controller_surface_events,
};

static const struct wl_message ivi_controller_screen_requests[] = {
	{ "destroy", "", types + 0 },
	{ "clear", "", types + 0 },
	{ "add_layer", "o", types + 16 },
	{ "screenshot", "s", types + 0 },
	{ "set_render_order", "a", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_controller_screen_interface = {
	"ivi_controller_screen", 1,
	5, ivi_controller_screen_requests,
	0, NULL,
};

static const struct wl_message ivi_share_requests[] = {
	{ "get_ivi_share_surface", "nu", types + 17 },
};

WL_EXPORT const struct wl_interface ivi_share_interface = {
	"ivi_share", 1,
	1, ivi_share_requests,
	0, NULL,
};

static const struct wl_message ivi_share_surface_requests[] = {
	{ "destroy", "", types + 0 },
	{ "redirect_touch_down", "uiff", types + 0 },
	{ "redirect_touch_up", "ui", types + 0 },
	{ "redirect_touch_motion", "iff", types + 0 },
	{ "redirect_touch_frame", "", types + 0 },
	{ "redirect_touch_cancel", "", types + 0 },
};

static const struct wl_message ivi_share_surface_events[] = {
	{ "damage", "u", types + 0 },
	{ "configure", "uuuuu", types + 0 },
	{ "input_capabilities", "u", types + 0 },
	{ "share_surface_state", "u", types + 0 },
};

WL_EXPORT const struct wl_interface ivi_share_surface_interface = {
	"ivi_share_surface", 1,
	6, ivi_share_surface_requests,
	4, ivi_share_surface_events,
};

