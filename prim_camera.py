from pxr import UsdGeom, Usd
from prim_xform import add_xform
import utils
import imp


def set_camera_focallength(xsi_camera, usd_camera, frame=None):
    xsi_focal_length = (xsi_camera.Parameters("projplanedist").Value if frame is None else xsi_camera.Parameters("projplanedist").GetValue2(frame))
    if frame is None:
        usd_camera.CreateFocalLengthAttr().Set(xsi_focal_length)
    else:
        usd_camera.CreateFocalLengthAttr().Set(xsi_focal_length, Usd.TimeCode(frame))


def set_camera_focusdistance(xsi_camera, usd_camera, frame=None):
    xsi_interest = xsi_camera.Interest
    # get global position of the camera and the interest
    xsi_camera_position = xsi_camera.Kinematics.Global.Transform.Translation if frame is None else xsi_camera.Kinematics.Local.GetTransform2(frame).Translation
    xsi_interest_position = xsi_interest.Kinematics.Global.Transform.Translation if frame is None else xsi_interest.Kinematics.Local.GetTransform2(frame).Translation
    if frame is None:
        usd_camera.CreateFocusDistanceAttr().Set(utils.get_distance(xsi_camera_position, xsi_interest_position))
    else:
        usd_camera.CreateFocusDistanceAttr().Set(utils.get_distance(xsi_camera_position, xsi_interest_position), Usd.TimeCode(frame))


def set_camera_clip_planes(xsi_camera, usd_camera, opt_animation):
    usd_clip_attribute = usd_camera.CreateClippingRangeAttr()
    if utils.is_param_animated(xsi_camera.Parameters("near"), opt_animation) or utils.is_param_animated(xsi_camera.Parameters("far"), opt_animation):
        for frame in range(opt_animation[0], opt_animation[1] + 1):
            usd_clip_attribute.Set((xsi_camera.Parameters("near").GetValue(frame), xsi_camera.Parameters("far").GetValue(frame)), Usd.TimeCode(frame))
    else:
        usd_clip_attribute.Set((xsi_camera.Parameters("near").Value, xsi_camera.Parameters("far").Value))


def add_camera(app, params, path_for_objects, stage, xsi_camera, root_path):
    imp.reload(utils)
    usd_xform, ref_stage, ref_stage_asset = add_xform(app, params, path_for_objects, True, stage, xsi_camera, root_path)
    usd_camera = UsdGeom.Camera.Define(ref_stage, str(usd_xform.GetPath()) + "/" + xsi_camera.Name)
    # set time independent attributes
    # perspective or ortographic
    if xsi_camera.Parameters("proj").Value == 0:
        usd_camera.CreateProjectionAttr().Set(UsdGeom.Tokens.orthographic)
    else:
        usd_camera.CreateProjectionAttr().Set(UsdGeom.Tokens.perspective)

    opt_animation = params.get("animation", None)
    set_camera_clip_planes(xsi_camera, usd_camera, opt_animation)

    # visibility
    xsi_vis_prop = xsi_camera.Properties("Visibility")
    usd_camera.CreateVisibilityAttr().Set(UsdGeom.Tokens.invisible if xsi_vis_prop.Parameters("viewvis").Value is False else UsdGeom.Tokens.inherited)

    # aperture size, w = 1024 pixels
    xsi_w = 1024
    xsi_aspect = xsi_camera.Parameters("aspect").Value
    usd_camera.CreateHorizontalApertureAttr().Set(xsi_w)
    usd_camera.CreateVerticalApertureAttr().Set(xsi_w / xsi_aspect)
    # offset is zero
    usd_camera.CreateHorizontalApertureOffsetAttr().Set(0)
    usd_camera.CreateVerticalApertureOffsetAttr().Set(0)

    if opt_animation is None or not utils.is_focallength_animated(xsi_camera, opt_animation):
        set_camera_focallength(xsi_camera, usd_camera)
    else:
        for frame in range(opt_animation[0], opt_animation[1] + 1):
            set_camera_focallength(xsi_camera, usd_camera, frame)

    if opt_animation is None or not utils.is_focusdistance_animated(xsi_camera, opt_animation):
        set_camera_focusdistance(xsi_camera, usd_camera)
    else:
        for frame in range(opt_animation[0], opt_animation[1] + 1):
            set_camera_focusdistance(xsi_camera, usd_camera, frame)
    ref_stage.Save()

    return stage.GetPrimAtPath(root_path + str(usd_xform.GetPath()))


def import_set_interest_at_frame(app, xsi_camera, xsi_interest, distance, usd_tfm, frame=None):
    # if frame is None, then this is static value, in other case we should create the animation key
    # calculate osition of the iterest point, for this we should get direction of the camera
    direction = utils.get_normalized(usd_tfm.GetRow(2))
    camera_position = usd_tfm.GetRow(3)
    interest_poisition = (camera_position[0] - distance * direction[0], camera_position[1] - distance * direction[1], camera_position[2] - distance * direction[2])
    if frame is None:
        new_transfrom = xsi_interest.Kinematics.Local.Transform
        new_transfrom.SetTranslationFromValues(interest_poisition[0], interest_poisition[1], interest_poisition[2])
        xsi_interest.Kinematics.Local.Transform = new_transfrom
    else:
        new_transfrom = xsi_interest.Kinematics.Local.Transform
        xsi_translation = new_transfrom.Translation
        app.SaveKey(xsi_interest.Name + ".kine.local.posx", frame, xsi_translation.X)
        app.SaveKey(xsi_interest.Name + ".kine.local.posy", frame, xsi_translation.Y)
        app.SaveKey(xsi_interest.Name + ".kine.local.posz", frame, xsi_translation.Z)


def import_define_camera(app, xsi_camera, xsi_interest, usd_camera, usd_tfm):
    usd_clip_range = usd_camera.GetClippingRangeAttr()
    usd_clip_range_time = usd_clip_range.GetTimeSamples()
    if len(usd_clip_range_time) <= 1:
        usd_clip_range_value = usd_clip_range.Get()
        xsi_camera.Parameters("near").Value = usd_clip_range_value[0]
        xsi_camera.Parameters("far").Value = usd_clip_range_value[1]
    else:
        for frame in usd_clip_range_time:
            usd_clip_range_value = usd_clip_range.Get(frame)
            app.SaveKey(xsi_camera.Parameters("near"), frame, usd_clip_range_value[0])
            app.SaveKey(xsi_camera.Parameters("far"), frame, usd_clip_range_value[1])

    usd_focal_length = usd_camera.GetFocalLengthAttr()
    usd_focal_length_time = usd_focal_length.GetTimeSamples()
    if len(usd_focal_length_time) <= 1:
        xsi_camera.Parameters("projplanedist").Value = usd_focal_length.Get()
    else:
        for frame in usd_focal_length_time:
            app.SaveKey(xsi_camera.Parameters("projplanedist"), frame, usd_focal_length.Get(frame))

    usd_projection = usd_camera.GetProjectionAttr().Get()
    xsi_camera.Parameters("proj").Value = 0 if usd_projection == "orthographic" else 1

    # aspect is not animated, so, use only the first value for ii
    usd_horizontal = usd_camera.GetHorizontalApertureAttr().Get()
    usd_vertical = usd_camera.GetVerticalApertureAttr().Get()
    xsi_camera.Parameters("aspect").Value = float(usd_horizontal) / float(usd_vertical)

    # finally set interest point from focus distance
    if xsi_interest is not None:
        usd_focus = usd_camera.GetFocusDistanceAttr()
        usd_focus_time = usd_focus.GetTimeSamples()
        if len(usd_focus_time) <= 1:
            import_set_interest_at_frame(app, xsi_camera, xsi_interest, usd_focus.Get(), usd_tfm[0])
        else:
            for frame in usd_focus_time:
                frame_index = utils.get_index_in_frames_array(usd_tfm[1], frame)
                import_set_interest_at_frame(app, xsi_camera, xsi_interest, usd_focus.Get(frame), usd_tfm[0][frame_index if frame_index > -1 else 0], frame=frame)


def emit_camera(app, options, camera_name, usd_tfm, visibility, usd_prim, xsi_parent):
    # save old childrens
    children_ids = []
    for child in xsi_parent.Children:
        children_ids.append(child.ObjectID)

    # create the camera
    xsi_camera = xsi_parent.AddCamera("Camera", camera_name)

    xsi_interest = None
    for ch in xsi_parent.Children:
        if ch.Type == "CameraInterest" and ch.ObjectId not in children_ids:
            xsi_interest = ch

    usd_camera = UsdGeom.Camera(usd_prim)
    utils.set_xsi_transform(app, xsi_camera, usd_tfm)
    utils.set_xsi_visibility(xsi_camera, visibility)
    if xsi_interest is not None:
        utils.set_xsi_visibility(xsi_interest, visibility)

    import_define_camera(app, xsi_camera, xsi_interest, usd_camera, usd_tfm)

    return xsi_camera
