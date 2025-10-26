from kivy.logger import Logger

from backend.files import fflags, settings
from frontend.gui.elements import (
    ExtendedButton,
    SectionText,
    BasicScreen,
    ExtendedToggle,
    DropdownItem,
    ExtendedDropdown,
    ExtendedTextField
)

TAG = "DBFFlagsScreen" + ": "

__all__ = ["PlayLogs"]

class FFlags(BasicScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "FastFlags",
            id = "FastFlagsScreen",
            *args, **kwargs
        )
        self.add_widgets(
            SectionText("Advanced"),
            ExtendedButton(
                icon = "pencil",
                title = "Fast Flag Editor",
                subtitle = "Manage your own Fast Flags. Use with caution.",
                callback = self._goToFFlagsEditor
            ),
            ExtendedToggle(
                title = "Allow DroidBlox to manage Fast Flags",
                subtitle = "Disabling this will prevent anything configured here from being applied to Roblox.",
                callback = lambda value: (
                    settings.writeSetting("applyFFlags", value)
                ),
                id = "applyFFlags"
            ),
            SectionText("Presets"),
            ExtendedToggle(
                title = "Disable Roblox telemetry",
                subtitle = "Note this disables only some of the Roblox telemetry.",
                callback = lambda value: (
                    fflags.mergeFFlags({
                        "FFlagDebugDisableTelemetryEphemeralCounter": "True",
                        "FFlagDebugDisableTelemetryEphemeralStat": "True",
                        "FFlagDebugDisableTelemetryEventIngest": "True",
                        "FFlagDebugDisableTelemetryV2Counter": "True",
                        "FFlagDebugDisableTelemetryV2Event": "True",
                        "FFlagDebugDisableTelemetryV2Stat": "True"
                    }) if value else fflags.deleteFFlags([
                        "FFlagDebugDisableTelemetryEphemeralCounter",
                        "FFlagDebugDisableTelemetryEphemeralStat",
                        "FFlagDebugDisableTelemetryEventIngest",
                        "FFlagDebugDisableTelemetryV2Counter",
                        "FFlagDebugDisableTelemetryV2Event",
                        "FFlagDebugDisableTelemetryV2Stat"
                    ])
                ),
                id = "disableRobloxTelemetry"
            ),
            SectionText("Rendering and Graphics"),
            ExtendedDropdown(
                title = "Anti-aliasing quality (MSAA)",
                subtitle = "Smoothens the jagged edges to make textures detailed. This may impact your gaming experience depending on your device.",
                items = [
                    DropdownItem("Automatic", onRelease = lambda: (
                        fflags.deleteFFlags(["FIntDebugForceMSAASamples"])
                    )),
                    DropdownItem("1x", onRelease = lambda: (
                        fflags.writeFFlag("FIntDebugForceMSAASamples", "1")
                    )),
                    DropdownItem("2x", onRelease = lambda: (
                        fflags.writeFFlag("FIntDebugForceMSAASamples", "2")
                    )), 
                    DropdownItem("4x", onRelease = lambda: (
                        fflags.writeFFlag("FIntDebugForceMSAASamples", "4")
                    ))
                ],
                default = "Automatic",
                id = "antiAliasingQuality"
            ),
            ExtendedToggle(
                title = "Disable player shadows",
                subtitle = "Disables the shadow on players.",
                callback = lambda value: (
                    fflags.writeFFlag("FIntRenderShadowIntensity", 0) if value else fflags.deleteFFlags(["FIntRenderShadowIntensity"])
                ),
                id = "disablePlayerShadows"
            ),
            ExtendedToggle(
                title = "Disable post-processing effects",
                subtitle = "Disables post-processing effects (e.g. sun rays, depth of field element, etc). " +
                            self.createRef("https://create.roblox.com/docs/environment/post-processing-effects"),
                callback = lambda value: (
                    fflags.writeFFlag("FFlagDisablePostFx", "True") if value else fflags.deleteFFlags(["FFlagDisablePostFx"])
                ),
                id = "disablePostProcessingEffects"
            ),
            ExtendedToggle(
                title = "Disable terrain textures",
                subtitle = "Dont render terrain textures",
                callback = lambda value: (
                    fflags.writeFFlag("FIntTerrainArraySliceSize", "0") if value else fflags.deleteFFlags(["FIntTerrainArraySliceSize"])
                ),
                id = "disableTerrainTextures"
            ),
            ExtendedTextField(
                title = "Framerate limit",
                subtitle = "Set the framerate limit for Roblox. " +
                            self.createRef("https://github.com/bloxstraplabs/bloxstrap/wiki/A-guide-to-FastFlags#framerate-limit"),
                callback = lambda value: (
                    fflags.writeFFlag("DFIntTaskSchedulerTargetFps", value) if value else fflags.deleteFFlags(["DFIntTaskSchedulerTargetFps"])
                ),
                id = "framerateLimit"
            ),
            ExtendedDropdown(
                title = "Preferred lighting technology",
                subtitle = "Choose which lighting technology should be forced in games. Might cause lighting issues! " +
                            self.createRef("https://github.com/bloxstraplabs/bloxstrap/wiki/A-guide-to-FastFlags#preferred-lighting-technology"),
                items = [
                    DropdownItem("Chosen by game", onRelease = lambda: (
                        fflags.deleteFFlags([
                            "DFFlagDebugRenderForceTechnologyVoxel",
                            "FFlagDebugForceFutureIsBrightPhase2",
                            "FFlagDebugForceFutureIsBrightPhase3"
                        ])
                    )),
                    DropdownItem("Voxel (Phase 1)", onRelease = lambda: (
                        fflags.writeFFlag("DFFlagDebugRenderForceTechnologyVoxel", True),
                        fflags.deleteFFlags([
                            "FFlagDebugForceFutureIsBrightPhase2",
                            "FFlagDebugForceFutureIsBrightPhase3"
                        ])
                    )),
                    DropdownItem("Shadow Map (Phase 2)", onRelease = lambda: (
                        fflags.writeFFlag("FFlagDebugForceFutureIsBrightPhase2", True),
                        fflags.deleteFFlags([
                            "DFFlagDebugRenderForceTechnologyVoxel",
                            "FFlagDebugForceFutureIsBrightPhase3"
                        ])
                    )),
                    DropdownItem("Future (Phase 3), ", onRelease = lambda: (
                        fflags.writeFFlag("FFlagDebugForceFutureIsBrightPhase3", True),
                        fflags.deleteFFlags([
                            "FFlagDebugForceFutureIsBrightPhase2",
                            "DFFlagDebugRenderForceTechnologyVoxel"
                        ])
                    ))
                ],
                default = "Chosen by game",
                id = "preferredLightingTechnology"
            ),
            ExtendedDropdown(
                title = "Rendering mode",
                subtitle = "Choose what rendering api to use for Roblox",
                items = [
                    DropdownItem("Automatic", onRelease = lambda: (
                        fflags.deleteFFlags([
                            "FFlagDebugGraphicsPreferVulkan",
                            "FFlagDebugGraphicsPreferOpenGL"
                        ])
                    )),
                    DropdownItem("Vulkan", onRelease = lambda: (
                        fflags.writeFFlag("FFlagDebugGraphicsPreferVulkan", "True"),
                        fflags.deleteFFlags(["FFlagDebugGraphicsPreferOpenGL"])
                    )),
                    DropdownItem("OpenGL", onRelease = lambda: (
                        fflags.writeFFlag("FFlagDebugGraphicsPreferOpenGL", "True"),
                        fflags.deleteFFlags(["FFlagDebugGraphicsPreferVulkan"])
                    )),
                ],
                default = "Automatic",
                id = "renderingMode"
            ),
            ExtendedDropdown(
                title = "Texture quality",
                subtitle = "Choose what level of texture quality to render",
                items = [
                    DropdownItem("Automatic", onRelease = lambda: (
                        fflags.deleteFFlags([
                            "DFFlagTextureQualityOverrideEnabled",
                            "DFIntTextureQualityOverride"
                        ])
                    )),
                    DropdownItem("Level 0 (lowest)", onRelease = lambda: (
                        fflags.mergeFFlags({
                            "DFFlagTextureQualityOverrideEnabled": "True",
                            "DFIntTextureQualityOverride": "0"
                        })
                    )),
                    DropdownItem("Level 1 ", onRelease = lambda: (
                        fflags.mergeFFlags({
                            "DFFlagTextureQualityOverrideEnabled": "True",
                            "DFIntTextureQualityOverride": "1"
                        })
                    )),
                    DropdownItem("Level 2", onRelease = lambda: (
                        fflags.mergeFFlags({
                            "DFFlagTextureQualityOverrideEnabled": "True",
                            "DFIntTextureQualityOverride": "2"
                        })
                    )),
                    DropdownItem("Level 3 (highest)", onRelease = lambda: (
                        fflags.mergeFFlags({
                            "DFFlagTextureQualityOverrideEnabled": "True",
                            "DFIntTextureQualityOverride": "3"
                        })
                    ))
                ],
                default = "Automatic",
                id = "textureQuality"
            ),
            SectionText("User Interface and Layout"),
            ExtendedTextField(
                title = "Hiding GUIs",
                subtitle = "Toggled with " + self.createRef("https://bloxstraplabs.com/wiki/features/engine-settings/#gui-hiding", "keyboard shortcuts (might require using an OTG).") +
                            " Input id of a group you're in.",
                callback = lambda value: (
                    fflags.mergeFFlags({
                        "DFIntCanHideGuiGroupId": value,
                        "FFlagUserShowGuiHideToggles": True
                    }) if value else fflags.deleteFFlags([
                        "DFIntCanHideGuiGroupId",
                        "FFlagUserShowGuiHideToggles"
                    ])
                ),
                id = "hideGui"
            ),
            ExtendedTextField(
                title = "Font size",
                subtitle = "Default is 1",
                callback = lambda value: (
                    fflags.writeFFlag("FIntFontSizePadding", value) if value else fflags.deleteFFlags(["FIntFontSizePadding"])
                ),
                id = "fontSize"
            ),
            SectionText("Debloat Roblox Menu"),
            ExtendedToggle(
                title = "VR Toggle",
                subtitle = "Remove VR Toggle",
                callback = lambda value: (
                    fflags.writeFFlag("FFlagAlwaysShowVRToggleV3", "False") if value else fflags.deleteFFlags(["FFlagAlwaysShowVRToggleV3"])
                ),
                id = "removeVrToggle"
            ),
            ExtendedToggle(
                title = "Feedback button",
                subtitle = "Remove Feedback button",
                callback = lambda value: (
                    fflags.writeFFlag("FFlagDisableFeedbackSoothsayerCheck", "True") if value else fflags.removeFFlags(["FFlagDisableFeedbackSoothsayerCheck"])
                ),
                id = "removeFeedbackButton"
            ),
            ExtendedToggle(
                title = "Language selector",
                subtitle = "Remove Language selector",
                callback = lambda value: (
                    fflags.writeFFlag("FIntV1MenuLanguageSelectionFeaturePerMillageRollout", "0") if value else fflags.removeFFlags(["FIntV1MenuLanguageSelectionFeaturePerMillageRollout"])
                ),
                id = "removeLanguageSelector"
            ),
            ExtendedToggle(
                title = "Framerate cap",
                subtitle = "Remove Framerate cap",
                callback = lambda value: (
                    fflags.writeFFlag("FFlagGameBasicSettingsFramerateCap5", "False") if value else fflags.removeFFlags(["FFlagGameBasicSettingsFramerateCap5"])
                ),
                id = "removeFramerateCap"
            ),
            ExtendedToggle(
                title = "Chat translation",
                subtitle = "Remove Chat translation",
                callback = lambda value: (
                    fflags.writeFFlag("FFlagChatTranslationSettingEnabled3", "False") if value else fflags.removeFFlags(["FFlagChatTranslationSettingEnabled3"])
                ),
                id = "removeChatTranslation"
            ),
            SectionText("FLog Debug"),
            ExtendedTextField(
                title = "Flag State",
                subtitle = "Show values of specified flags during runtime. Each flag is comma separated.",
                callback = lambda value: (
                    fflags.writeFFlag("FStringDebugShowFlagState", value) if value else fflags.deleteFFlags(["FStringDebugShowFlagState"])
                ),
                id = "flagState"
            ),
            ExtendedToggle(
                title = "Ping breakdown",
                subtitle = "Sends ping information to the Roblox console.",
                callback = lambda value: (
                    fflags.writeFFlag("DFFlagDebugPrintDataPingBreakDown", "False") if value else fflags.removeFFlags(["DFFlagDebugPrintDataPingBreakDown"])
                ),
                id = "pingBreakdown"
            )
        )

    def _goToFFlagsEditor(self, *args):
        Logger.debug(TAG + "Going to fflag editor screen")
        self.parent.parent.get_ids().ScreenManager.current = "FastFlagsEditor"