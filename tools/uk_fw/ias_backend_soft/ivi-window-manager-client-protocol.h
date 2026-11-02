/*
 */

#ifndef IVI_WINDOW_MANAGER_CLIENT_PROTOCOL_H
#define IVI_WINDOW_MANAGER_CLIENT_PROTOCOL_H

#ifdef  __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include "wayland-client.h"

struct wl_client;
struct wl_resource;

struct ivi_hmi_client;
struct ivi_hmi_receiver;
struct ivi_hmi_requester;
struct ivi_info_receiver;
struct ivi_info_requester;
struct ivi_window_manager;

extern const struct wl_interface ivi_window_manager_interface;
extern const struct wl_interface ivi_hmi_receiver_interface;
extern const struct wl_interface ivi_hmi_requester_interface;
extern const struct wl_interface ivi_hmi_client_interface;
extern const struct wl_interface ivi_info_receiver_interface;
extern const struct wl_interface ivi_info_requester_interface;

#ifndef IVI_WINDOW_MANAGER_FULL_SCREEN_MASK_ENUM
#define IVI_WINDOW_MANAGER_FULL_SCREEN_MASK_ENUM
enum ivi_window_manager_full_screen_mask {
	IVI_WINDOW_MANAGER_FULL_SCREEN_MASK_DRAWER = 1,
	IVI_WINDOW_MANAGER_FULL_SCREEN_MASK_STATUSBAR = 2,
};
#endif /* IVI_WINDOW_MANAGER_FULL_SCREEN_MASK_ENUM */

#ifndef IVI_WINDOW_MANAGER_APP_TYPE_ENUM
#define IVI_WINDOW_MANAGER_APP_TYPE_ENUM
enum ivi_window_manager_app_type {
	IVI_WINDOW_MANAGER_APP_TYPE_NONE = 0,
	IVI_WINDOW_MANAGER_APP_TYPE_STATUSBAR = 1,
	IVI_WINDOW_MANAGER_APP_TYPE_POPUP = 2,
	IVI_WINDOW_MANAGER_APP_TYPE_KEYBOARD = 3,
	IVI_WINDOW_MANAGER_APP_TYPE_BACKGROUND = 4,
	IVI_WINDOW_MANAGER_APP_TYPE_VOLUME_OSD = 5,
	IVI_WINDOW_MANAGER_APP_TYPE_AV_OSD = 6,
	IVI_WINDOW_MANAGER_APP_TYPE_MAX = 7,
};
#endif /* IVI_WINDOW_MANAGER_APP_TYPE_ENUM */

/**
 * ivi_window_manager - window manager api
 * @primary_screen_size: primary screen size
 *
 * 
 */
struct ivi_window_manager_listener {
	/**
	 * primary_screen_size - primary screen size
	 * @width: (none)
	 * @height: (none)
	 *
	 * 
	 */
	void (*primary_screen_size)(void *data,
				    struct ivi_window_manager *ivi_window_manager,
				    uint32_t width,
				    uint32_t height);
};

static inline int
ivi_window_manager_add_listener(struct ivi_window_manager *ivi_window_manager,
				const struct ivi_window_manager_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_window_manager,
				     (void (**)(void)) listener, data);
}

#define IVI_WINDOW_MANAGER_UPDATE_LAYOUT	0
#define IVI_WINDOW_MANAGER_GET_PRIMARY_SCREEN_SIZE	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_VISIBLE	2
#define IVI_WINDOW_MANAGER_REQUEST_FG	3
#define IVI_WINDOW_MANAGER_SHOW_NOTIFICATION	4
#define IVI_WINDOW_MANAGER_SHOW_PAS	5
#define IVI_WINDOW_MANAGER_SET_SURFACE_LAYOUT	6
#define IVI_WINDOW_MANAGER_SET_SURFACE_ALPHA	7
#define IVI_WINDOW_MANAGER_SET_VISIBLE_FOR_QTWAYLAND	8
#define IVI_WINDOW_MANAGER_EXPAND_DRAWER	9
#define IVI_WINDOW_MANAGER_SET_SURFACE_TO_TOP_ORDER_WITHIN_LAYER	10
#define IVI_WINDOW_MANAGER_SET_PARENT_CHILD_SURFACE	11
#define IVI_WINDOW_MANAGER_SET_SURFACE_TO_FULL_SCREEN	12
#define IVI_WINDOW_MANAGER_REQUEST_FG_WITH_APP_ID	13
#define IVI_WINDOW_MANAGER_SET_SURFACE_TO_FULL_SCREEN_WITH_APP_ID	14
#define IVI_WINDOW_MANAGER_SET_APP_NAME_WITH_APP_TYPE	15
#define IVI_WINDOW_MANAGER_SHOW_APP_WITH_APP_TYPE	16
#define IVI_WINDOW_MANAGER_SET_SURFACE_POSITION_WITH_APP_ID	17
#define IVI_WINDOW_MANAGER_REQUEST_CLONE_SURFACE_CREATE	18
#define IVI_WINDOW_MANAGER_SET_CLONE_SURFACE_LAYOUT	19
#define IVI_WINDOW_MANAGER_REQUEST_CLONE_SURFACE_DESTROY	20
#define IVI_WINDOW_MANAGER_REQUEST_MOVE_LAYER	21

#define IVI_WINDOW_MANAGER_UPDATE_LAYOUT_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_GET_PRIMARY_SCREEN_SIZE_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_VISIBLE_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_REQUEST_FG_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SHOW_NOTIFICATION_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SHOW_PAS_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_LAYOUT_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_ALPHA_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_VISIBLE_FOR_QTWAYLAND_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_EXPAND_DRAWER_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_TO_TOP_ORDER_WITHIN_LAYER_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_PARENT_CHILD_SURFACE_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_TO_FULL_SCREEN_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_REQUEST_FG_WITH_APP_ID_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_TO_FULL_SCREEN_WITH_APP_ID_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_APP_NAME_WITH_APP_TYPE_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SHOW_APP_WITH_APP_TYPE_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_SURFACE_POSITION_WITH_APP_ID_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_REQUEST_CLONE_SURFACE_CREATE_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_SET_CLONE_SURFACE_LAYOUT_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_REQUEST_CLONE_SURFACE_DESTROY_SINCE_VERSION	1
#define IVI_WINDOW_MANAGER_REQUEST_MOVE_LAYER_SINCE_VERSION	1

static inline void
ivi_window_manager_set_user_data(struct ivi_window_manager *ivi_window_manager, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_window_manager, user_data);
}

static inline void *
ivi_window_manager_get_user_data(struct ivi_window_manager *ivi_window_manager)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_window_manager);
}

static inline uint32_t
ivi_window_manager_get_version(struct ivi_window_manager *ivi_window_manager)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_window_manager);
}

static inline void
ivi_window_manager_destroy(struct ivi_window_manager *ivi_window_manager)
{
	wl_proxy_destroy((struct wl_proxy *) ivi_window_manager);
}

static inline void
ivi_window_manager_update_layout(struct ivi_window_manager *ivi_window_manager, uint32_t arg)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_UPDATE_LAYOUT, arg);
}

static inline void
ivi_window_manager_get_primary_screen_size(struct ivi_window_manager *ivi_window_manager)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_GET_PRIMARY_SCREEN_SIZE);
}

static inline void
ivi_window_manager_set_surface_visible(struct ivi_window_manager *ivi_window_manager, uint32_t surface_id, uint32_t is_visible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_VISIBLE, surface_id, is_visible);
}

static inline void
ivi_window_manager_request_fg(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, uint32_t surface_id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_REQUEST_FG, display_plane_idx, surface_id);
}

static inline void
ivi_window_manager_show_notification(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, uint32_t is_visible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SHOW_NOTIFICATION, display_plane_idx, is_visible);
}

static inline void
ivi_window_manager_show_PAS(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, uint32_t is_visible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SHOW_PAS, display_plane_idx, is_visible);
}

static inline void
ivi_window_manager_set_surface_layout(struct ivi_window_manager *ivi_window_manager, uint32_t surface_id, int32_t x, int32_t y, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_LAYOUT, surface_id, x, y, width, height);
}

static inline void
ivi_window_manager_set_surface_alpha(struct ivi_window_manager *ivi_window_manager, uint32_t surface_id, int32_t alpha)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_ALPHA, surface_id, alpha);
}

static inline void
ivi_window_manager_set_visible_for_qtwayland(struct ivi_window_manager *ivi_window_manager, uint32_t surface_id, int32_t isVisible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_VISIBLE_FOR_QTWAYLAND, surface_id, isVisible);
}

static inline void
ivi_window_manager_expand_drawer(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, int32_t isOn)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_EXPAND_DRAWER, display_plane_idx, isOn);
}

static inline void
ivi_window_manager_set_surface_to_top_order_within_layer(struct ivi_window_manager *ivi_window_manager, uint32_t surface_id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_TO_TOP_ORDER_WITHIN_LAYER, surface_id);
}

static inline void
ivi_window_manager_set_parent_child_surface(struct ivi_window_manager *ivi_window_manager, uint32_t parent_surface_id, uint32_t child_surface_id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_PARENT_CHILD_SURFACE, parent_surface_id, child_surface_id);
}

static inline void
ivi_window_manager_set_surface_to_full_screen(struct ivi_window_manager *ivi_window_manager, uint32_t surface_id, int32_t isFullScreen, uint32_t fullScreenMask)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_TO_FULL_SCREEN, surface_id, isFullScreen, fullScreenMask);
}

static inline void
ivi_window_manager_request_fg_with_app_id(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, const char *app_id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_REQUEST_FG_WITH_APP_ID, display_plane_idx, app_id);
}

static inline void
ivi_window_manager_set_surface_to_full_screen_with_app_id(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, const char *app_id, int32_t isFullScreen, uint32_t fullScreenMask)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_TO_FULL_SCREEN_WITH_APP_ID, display_plane_idx, app_id, isFullScreen, fullScreenMask);
}

static inline void
ivi_window_manager_set_app_name_with_app_type(struct ivi_window_manager *ivi_window_manager, uint32_t app_type, const char *app_id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_APP_NAME_WITH_APP_TYPE, app_type, app_id);
}

static inline void
ivi_window_manager_show_app_with_app_type(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, uint32_t app_type, uint32_t is_visible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SHOW_APP_WITH_APP_TYPE, display_plane_idx, app_type, is_visible);
}

static inline void
ivi_window_manager_set_surface_position_with_app_id(struct ivi_window_manager *ivi_window_manager, int32_t display_plane_idx, const char *app_id, int32_t x, int32_t y)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_SURFACE_POSITION_WITH_APP_ID, display_plane_idx, app_id, x, y);
}

static inline void
ivi_window_manager_request_clone_surface_create(struct ivi_window_manager *ivi_window_manager, uint32_t original_id, uint32_t clone_id, uint32_t display_id, int32_t x, int32_t y, int32_t w, int32_t h)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_REQUEST_CLONE_SURFACE_CREATE, original_id, clone_id, display_id, x, y, w, h);
}

static inline void
ivi_window_manager_set_clone_surface_layout(struct ivi_window_manager *ivi_window_manager, uint32_t clone_id, int32_t x, int32_t y, int32_t w, int32_t h)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_SET_CLONE_SURFACE_LAYOUT, clone_id, x, y, w, h);
}

static inline void
ivi_window_manager_request_clone_surface_destroy(struct ivi_window_manager *ivi_window_manager, uint32_t clone_id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_REQUEST_CLONE_SURFACE_DESTROY, clone_id);
}

static inline void
ivi_window_manager_request_move_layer(struct ivi_window_manager *ivi_window_manager, int32_t layer_id, int32_t dest_x, int32_t dest_y, int32_t duration)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_window_manager,
			 IVI_WINDOW_MANAGER_REQUEST_MOVE_LAYER, layer_id, dest_x, dest_y, duration);
}

/**
 * ivi_hmi_receiver - receive on HMI side
 * @receive_id: Receive id from window manager
 *
 * 
 */
struct ivi_hmi_receiver_listener {
	/**
	 * receive_id - Receive id from window manager
	 * @id: (none)
	 *
	 * 
	 */
	void (*receive_id)(void *data,
			   struct ivi_hmi_receiver *ivi_hmi_receiver,
			   uint32_t id);
};

static inline int
ivi_hmi_receiver_add_listener(struct ivi_hmi_receiver *ivi_hmi_receiver,
			      const struct ivi_hmi_receiver_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_hmi_receiver,
				     (void (**)(void)) listener, data);
}

#define IVI_HMI_RECEIVER_DESTROY	0

#define IVI_HMI_RECEIVER_DESTROY_SINCE_VERSION	1

static inline void
ivi_hmi_receiver_set_user_data(struct ivi_hmi_receiver *ivi_hmi_receiver, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_hmi_receiver, user_data);
}

static inline void *
ivi_hmi_receiver_get_user_data(struct ivi_hmi_receiver *ivi_hmi_receiver)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_hmi_receiver);
}

static inline uint32_t
ivi_hmi_receiver_get_version(struct ivi_hmi_receiver *ivi_hmi_receiver)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_hmi_receiver);
}

static inline void
ivi_hmi_receiver_destroy(struct ivi_hmi_receiver *ivi_hmi_receiver)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_hmi_receiver,
			 IVI_HMI_RECEIVER_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_hmi_receiver);
}

#ifndef IVI_HMI_REQUESTER_APP_TYPE_ENUM
#define IVI_HMI_REQUESTER_APP_TYPE_ENUM
enum ivi_hmi_requester_app_type {
	IVI_HMI_REQUESTER_APP_TYPE_DEFAULT = 0,
	IVI_HMI_REQUESTER_APP_TYPE_QT = 1,
	IVI_HMI_REQUESTER_APP_TYPE_GSTREAMER = 2,
};
#endif /* IVI_HMI_REQUESTER_APP_TYPE_ENUM */

#define IVI_HMI_REQUESTER_DESTROY	0
#define IVI_HMI_REQUESTER_CREATE_HMI_CLIENT	1
#define IVI_HMI_REQUESTER_REQUEST_ID	2
#define IVI_HMI_REQUESTER_RESERVE_ID	3

#define IVI_HMI_REQUESTER_DESTROY_SINCE_VERSION	1
#define IVI_HMI_REQUESTER_CREATE_HMI_CLIENT_SINCE_VERSION	1
#define IVI_HMI_REQUESTER_REQUEST_ID_SINCE_VERSION	1
#define IVI_HMI_REQUESTER_RESERVE_ID_SINCE_VERSION	1

static inline void
ivi_hmi_requester_set_user_data(struct ivi_hmi_requester *ivi_hmi_requester, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_hmi_requester, user_data);
}

static inline void *
ivi_hmi_requester_get_user_data(struct ivi_hmi_requester *ivi_hmi_requester)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_hmi_requester);
}

static inline uint32_t
ivi_hmi_requester_get_version(struct ivi_hmi_requester *ivi_hmi_requester)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_hmi_requester);
}

static inline void
ivi_hmi_requester_destroy(struct ivi_hmi_requester *ivi_hmi_requester)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_hmi_requester,
			 IVI_HMI_REQUESTER_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_hmi_requester);
}

static inline struct ivi_hmi_client *
ivi_hmi_requester_create_hmi_client(struct ivi_hmi_requester *ivi_hmi_requester, int32_t display_plane_idx, uint32_t surface_id, const char *app_id)
{
	struct wl_proxy *id;

	id = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_hmi_requester,
			 IVI_HMI_REQUESTER_CREATE_HMI_CLIENT, &ivi_hmi_client_interface, display_plane_idx, surface_id, app_id, NULL);

	return (struct ivi_hmi_client *) id;
}

static inline struct ivi_hmi_receiver *
ivi_hmi_requester_request_id(struct ivi_hmi_requester *ivi_hmi_requester, const char *name)
{
	struct wl_proxy *id;

	id = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_hmi_requester,
			 IVI_HMI_REQUESTER_REQUEST_ID, &ivi_hmi_receiver_interface, name, NULL);

	return (struct ivi_hmi_receiver *) id;
}

static inline struct ivi_hmi_receiver *
ivi_hmi_requester_reserve_id(struct ivi_hmi_requester *ivi_hmi_requester, uint32_t app_type_info, uint32_t surface_id)
{
	struct wl_proxy *id;

	id = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_hmi_requester,
			 IVI_HMI_REQUESTER_RESERVE_ID, &ivi_hmi_receiver_interface, app_type_info, surface_id, NULL);

	return (struct ivi_hmi_receiver *) id;
}

#define IVI_HMI_CLIENT_DESTROY	0
#define IVI_HMI_CLIENT_SET_APP_ID	1
#define IVI_HMI_CLIENT_SET_DISPLAY_PLANE	2

#define IVI_HMI_CLIENT_DESTROY_SINCE_VERSION	1
#define IVI_HMI_CLIENT_SET_APP_ID_SINCE_VERSION	1
#define IVI_HMI_CLIENT_SET_DISPLAY_PLANE_SINCE_VERSION	1

static inline void
ivi_hmi_client_set_user_data(struct ivi_hmi_client *ivi_hmi_client, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_hmi_client, user_data);
}

static inline void *
ivi_hmi_client_get_user_data(struct ivi_hmi_client *ivi_hmi_client)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_hmi_client);
}

static inline uint32_t
ivi_hmi_client_get_version(struct ivi_hmi_client *ivi_hmi_client)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_hmi_client);
}

static inline void
ivi_hmi_client_destroy(struct ivi_hmi_client *ivi_hmi_client)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_hmi_client,
			 IVI_HMI_CLIENT_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_hmi_client);
}

static inline void
ivi_hmi_client_set_app_id(struct ivi_hmi_client *ivi_hmi_client, const char *id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_hmi_client,
			 IVI_HMI_CLIENT_SET_APP_ID, id);
}

static inline void
ivi_hmi_client_set_display_plane(struct ivi_hmi_client *ivi_hmi_client, int32_t plane_idx)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_hmi_client,
			 IVI_HMI_CLIENT_SET_DISPLAY_PLANE, plane_idx);
}

/**
 * ivi_info_receiver - for receiving info on client side
 * @receive_BG_info: Receive surface ID and app ID that transit BG from
 *	window manager
 * @receive_FG_info: Receive surface ID and app ID that transition to FG
 *	is finished from window manager
 *
 * 
 */
struct ivi_info_receiver_listener {
	/**
	 * receive_BG_info - Receive surface ID and app ID that transit
	 *	BG from window manager
	 * @surface_id: (none)
	 * @plane_idx: (none)
	 * @app_id: (none)
	 *
	 * 
	 */
	void (*receive_BG_info)(void *data,
				struct ivi_info_receiver *ivi_info_receiver,
				uint32_t surface_id,
				int32_t plane_idx,
				const char *app_id);
	/**
	 * receive_FG_info - Receive surface ID and app ID that
	 *	transition to FG is finished from window manager
	 * @surface_id: (none)
	 * @plane_idx: (none)
	 * @app_id: (none)
	 *
	 * 
	 */
	void (*receive_FG_info)(void *data,
				struct ivi_info_receiver *ivi_info_receiver,
				uint32_t surface_id,
				int32_t plane_idx,
				const char *app_id);
};

static inline int
ivi_info_receiver_add_listener(struct ivi_info_receiver *ivi_info_receiver,
			       const struct ivi_info_receiver_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_info_receiver,
				     (void (**)(void)) listener, data);
}

#define IVI_INFO_RECEIVER_DESTROY	0

#define IVI_INFO_RECEIVER_DESTROY_SINCE_VERSION	1

static inline void
ivi_info_receiver_set_user_data(struct ivi_info_receiver *ivi_info_receiver, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_info_receiver, user_data);
}

static inline void *
ivi_info_receiver_get_user_data(struct ivi_info_receiver *ivi_info_receiver)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_info_receiver);
}

static inline uint32_t
ivi_info_receiver_get_version(struct ivi_info_receiver *ivi_info_receiver)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_info_receiver);
}

static inline void
ivi_info_receiver_destroy(struct ivi_info_receiver *ivi_info_receiver)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_info_receiver,
			 IVI_INFO_RECEIVER_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_info_receiver);
}

#define IVI_INFO_REQUESTER_DESTROY	0
#define IVI_INFO_REQUESTER_CREATE_INFO_RECEIVER	1

#define IVI_INFO_REQUESTER_DESTROY_SINCE_VERSION	1
#define IVI_INFO_REQUESTER_CREATE_INFO_RECEIVER_SINCE_VERSION	1

static inline void
ivi_info_requester_set_user_data(struct ivi_info_requester *ivi_info_requester, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_info_requester, user_data);
}

static inline void *
ivi_info_requester_get_user_data(struct ivi_info_requester *ivi_info_requester)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_info_requester);
}

static inline uint32_t
ivi_info_requester_get_version(struct ivi_info_requester *ivi_info_requester)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_info_requester);
}

static inline void
ivi_info_requester_destroy(struct ivi_info_requester *ivi_info_requester)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_info_requester,
			 IVI_INFO_REQUESTER_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_info_requester);
}

static inline struct ivi_info_receiver *
ivi_info_requester_create_info_receiver(struct ivi_info_requester *ivi_info_requester)
{
	struct wl_proxy *info_receiver;

	info_receiver = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_info_requester,
			 IVI_INFO_REQUESTER_CREATE_INFO_RECEIVER, &ivi_info_receiver_interface, NULL);

	return (struct ivi_info_receiver *) info_receiver;
}

#ifdef  __cplusplus
}
#endif

#endif
