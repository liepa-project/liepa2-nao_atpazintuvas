<?xml version="1.0" encoding="UTF-8" ?>
<Package name="libot_sample" format_version="5">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="test_dialog" src="test_dialog/test_dialog.dlg" />
    </Dialogs>
    <Resources />
    <Topics>
        <Topic name="test_dialog_enu" src="test_dialog/test_dialog_enu.top" topicName="test_dialog" language="en_US" nuance="enu" />
    </Topics>
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
