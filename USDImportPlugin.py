# USDExportPlugin
# Initial code generated by Softimage SDK Wizard
# Executed Mon May 4 17:54:03 UTC+0500 2020 by Shekn
#
# Tip: To add a command to this plug-in, right-click in the
# script editor and choose Tools > Add Command.
import win32com.client
from win32com.client import constants
import sys
import os
if __sipath__ not in sys.path:
    sys.path.append(__sipath__)
import import_processor
import utils
import imp

null = None
false = 0
true = 1
app = Application
DEBUG_MODE = False


def log(message):
    app.LogMessage(message)


def XSILoadPlugin(in_reg):
    in_reg.Author = "Shekn"
    in_reg.Name = "USDImportPlugin"
    in_reg.Major = 1
    in_reg.Minor = 0

    in_reg.RegisterCommand("USDImportCommand", "USDImportCommand")
    in_reg.RegisterCommand("USDImportOpen", "USDImportOpen")
    in_reg.RegisterMenu(constants.siMenuMainFileImportID, "USD Import", False, False)
    # RegistrationInsertionPoint - do not remove this line

    return True


def USDImport_Init(ctxt):
    menu = ctxt.source
    menu.AddCommandItem("Import USD...", "USDImportOpen")


def XSIUnloadPlugin(in_reg):
    strPluginName = in_reg.Name
    app.LogMessage(str(strPluginName) + str(" has been unloaded."), constants.siVerbose)
    return true


def USDImportCommand_Init(in_ctxt):
    command = in_ctxt.Source
    args = command.Arguments
    # init parameters of the command
    args.Add("file_path")
    args.Add("attributes")
    args.Add("object_types")
    args.Add("clear_scene")
    args.Add("is_materials")
    args.Add("light_mode")

    return True


def USDImportCommand_Execute(*args):
    app.LogMessage("USDImport_Execute called", constants.siVerbose)
    # read arguments of the command
    file_path = args[0]
    attributes = args[1] if args[1] is not None else ('uvmap', 'normal', 'color', 'weightmap', 'cluster', 'vertex_creases', 'edge_creases')
    object_types = args[2] if args[2] is not None else ("strands", constants.siModelType, constants.siNullPrimType, constants.siPolyMeshType, constants.siLightPrimType, constants.siCameraPrimType, "pointcloud")
    clear_scene = args[3] if args[3] is not None else False
    is_materials = args[4] if args[4] is not None else True
    light_mode = args[5] if args[5] is not None else 0  # default light mode use default lights

    import_options = {"clear_scene": clear_scene,
                      "is_materials": is_materials,
                      "attributes": attributes,
                      "object_types": object_types,
                      "light_mode": light_mode,
                      "XSIMath": XSIMath}
    if DEBUG_MODE:
        imp.reload(import_processor)

    if file_path is not None and len(file_path) > 0 and os.path.isfile(file_path):
        import_processor.import_usd(app, file_path, import_options, XSIUIToolkit)
    else:
        app.LogMessage("Select an *.usd file", constants.siWarning)

    return True


def USDImportOpen_Execute():
    if DEBUG_MODE:
        imp.reload(utils)

    scene_root = app.ActiveProject2.ActiveScene.Root

    plugin_path = utils.get_plugin_path(app, "USDImportPlugin")
    props_path = plugin_path + "import.props"
    if os.path.isfile(props_path):
        with open(props_path, "r") as file:
            import_props = eval(file.read())
    else:  # set default values
        import_props = {"clear_scene": False,
                        "materials": True,
                        "is_polymesh": True,
                        "is_lights": True,
                        "is_cameras": True,
                        "is_strands": True,
                        "is_pointclouds": True,
                        "is_nulls": True,
                        "is_models": True,
                        "is_uv_maps": True,
                        "is_normals": True,
                        "is_weightmaps": True,
                        "is_clusters": True,
                        "is_vertex_creases": True,
                        "is_edge_creases": True,
                        "is_vertex_color": True,
                        "light_mode": 0}

    # create property
    prop = scene_root.AddProperty("CustomProperty", False, "USD_Import")

    # add parameters
    prop.AddParameter3("file_path", constants.siString, "", "", "", False, False)
    param = prop.AddParameter3("clear_scene", constants.siBool, import_props["clear_scene"])
    param.Animatable = False
    param = prop.AddParameter3("materials", constants.siBool, import_props["materials"])
    param.Animatable = False

    param = prop.AddParameter3("is_polymesh", constants.siBool, import_props["is_polymesh"])
    param.Animatable = False
    param = prop.AddParameter3("is_lights", constants.siBool, import_props["is_lights"])
    param.Animatable = False
    param = prop.AddParameter3("is_cameras", constants.siBool, import_props["is_cameras"])
    param.Animatable = False
    param = prop.AddParameter3("is_strands", constants.siBool, import_props["is_strands"])
    param.Animatable = False
    param = prop.AddParameter3("is_pointclouds", constants.siBool, import_props["is_pointclouds"])
    param.Animatable = False
    param = prop.AddParameter3("is_nulls", constants.siBool, import_props["is_nulls"])
    param.Animatable = False
    param = prop.AddParameter3("is_models", constants.siBool, import_props["is_models"])
    param.Animatable = False

    param = prop.AddParameter3("is_uv_maps", constants.siBool, import_props["is_uv_maps"])
    param.Animatable = False
    param = prop.AddParameter3("is_normals", constants.siBool, import_props["is_normals"])
    param.Animatable = False
    param = prop.AddParameter3("is_weightmaps", constants.siBool, import_props["is_weightmaps"])
    param.Animatable = False
    param = prop.AddParameter3("is_clusters", constants.siBool, import_props["is_clusters"])
    param.Animatable = False
    param = prop.AddParameter3("is_vertex_creases", constants.siBool, import_props["is_vertex_creases"])
    param.Animatable = False
    param = prop.AddParameter3("is_edge_creases", constants.siBool, import_props["is_edge_creases"])
    param.Animatable = False
    param = prop.AddParameter3("is_vertex_color", constants.siBool, import_props["is_vertex_color"])
    param.Animatable = False

    param = prop.AddParameter3("light_mode", constants.siInt2, import_props["light_mode"])
    param.Animatable = False

    # define layout
    layout = prop.PPGLayout
    layout.Clear()
    layout.AddGroup("File Path")
    item = layout.AddItem("file_path", "File", constants.siControlFilePath)
    item.SetAttribute(constants.siUIOpenFile, True)
    item.SetAttribute(constants.siUIFileMustExist, False)
    filter_string = "USD files (*.usd *.usdc *.usda *.usdz)|*.usd:*.usdc:*.usda:*.usdz|"
    item.SetAttribute(constants.siUIFileFilter, filter_string)
    layout.EndGroup()

    layout.AddGroup("Objects to Import")
    layout.AddRow()
    layout.AddItem("is_nulls", "Null")
    layout.AddItem("is_polymesh", "Polygon Mesh")
    layout.AddItem("is_lights", "Lights")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_cameras", "Cameras")
    layout.AddItem("is_strands", "Strands")
    layout.AddItem("is_pointclouds", "Pointclouds")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_models", "Model")
    layout.AddSpacer()
    layout.AddSpacer()
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Mesh Attributes")
    layout.AddRow()
    layout.AddItem("is_uv_maps", "UV Map")
    layout.AddItem("is_normals", "Normals")
    layout.AddItem("is_vertex_color", "Vertex Color")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_weightmaps", "Weightmaps")
    layout.AddItem("is_clusters", "Polygon Clusters")
    layout.AddItem("is_vertex_creases", "Vertex Creases")
    layout.EndRow()
    layout.AddRow()
    layout.AddItem("is_edge_creases", "Edge Creases")
    layout.AddSpacer()
    layout.AddSpacer()
    layout.EndRow()
    layout.EndGroup()

    layout.AddGroup("Lights")
    layout.AddEnumControl("light_mode", ["Default", 0, "Sycles", 1] if utils.is_sycles_install(app) else ["Default", 0], "Light Sources")
    layout.EndGroup()

    layout.AddGroup("Options")
    layout.AddItem("clear_scene", "Clear Scene")
    layout.AddItem("materials", "Assign Imported Materials")
    layout.EndGroup()

    rtn = app.InspectObj(prop, "", "Import *.usd file...", constants.siModal, False)
    if rtn is False:
        import_props["clear_scene"] = prop.Parameters("clear_scene").Value
        import_props["materials"] = prop.Parameters("materials").Value
        import_props["is_polymesh"] = prop.Parameters("is_polymesh").Value
        import_props["is_lights"] = prop.Parameters("is_lights").Value
        import_props["is_cameras"] = prop.Parameters("is_cameras").Value
        import_props["is_strands"] = prop.Parameters("is_strands").Value
        import_props["is_pointclouds"] = prop.Parameters("is_pointclouds").Value
        import_props["is_nulls"] = prop.Parameters("is_nulls").Value
        import_props["is_models"] = prop.Parameters("is_models").Value
        import_props["is_uv_maps"] = prop.Parameters("is_uv_maps").Value
        import_props["is_normals"] = prop.Parameters("is_normals").Value
        import_props["is_weightmaps"] = prop.Parameters("is_weightmaps").Value
        import_props["is_clusters"] = prop.Parameters("is_clusters").Value
        import_props["is_vertex_creases"] = prop.Parameters("is_vertex_creases").Value
        import_props["is_edge_creases"] = prop.Parameters("is_edge_creases").Value
        import_props["is_vertex_color"] = prop.Parameters("is_vertex_color").Value
        import_props["light_mode"] = prop.Parameters("light_mode").Value
        with open(props_path, "w") as file:
            file.write(str(import_props))

        objects_types = []
        if prop.Parameters("is_nulls").Value:
            objects_types.append(constants.siNullPrimType)
        if prop.Parameters("is_polymesh").Value:
            objects_types.append(constants.siPolyMeshType)
        if prop.Parameters("is_lights").Value:
            objects_types.append(constants.siLightPrimType)
        if prop.Parameters("is_cameras").Value:
            objects_types.append(constants.siCameraPrimType)
        if prop.Parameters("is_strands").Value:
            objects_types.append("strands")
        if prop.Parameters("is_pointclouds").Value:
            objects_types.append("pointcloud")
        if prop.Parameters("is_models").Value:
            objects_types.append(constants.siModelType)

        attributes = []
        if prop.Parameters("is_uv_maps").Value:
            attributes.append("uvmap")
        if prop.Parameters("is_normals").Value:
            attributes.append("normal")
        if prop.Parameters("is_vertex_color").Value:
            attributes.append("color")
        if prop.Parameters("is_weightmaps").Value:
            attributes.append("weightmap")
        if prop.Parameters("is_clusters").Value:
            attributes.append("cluster")
        if prop.Parameters("is_vertex_creases").Value:
            attributes.append("vertex_creases")
        if prop.Parameters("is_edge_creases").Value:
            attributes.append("edge_creases")

        # click "ok", execute import command
        app.USDImportCommand(prop.Parameters("file_path").Value,
                             attributes,
                             objects_types,
                             prop.Parameters("clear_scene").Value,
                             prop.Parameters("materials").Value,
                             prop.Parameters("light_mode").Value)

    # delete dialog
    app.DeleteObj(prop)

    return True
