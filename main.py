import os
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction


class LwsmExtension(Extension):

  def __init__(self):
    super(LwsmExtension, self).__init__()
    self.presets_path = None
    self.all_filenames = []
    self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
    self.subscribe(PreferencesEvent, PreferencesEventListener())
    self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
  
  def set_presets_path(self, presets_path):
    self.presets_path = os.path.expanduser(presets_path)
  
  def set_lwsm_presets(self, presets_path):
    all_filenames = []
    try:
      filenames = next( os.walk( presets_path ) )[2]
    except:
      filenames = []

    for filename in filenames:
      if ".json" in filename:
        generated_name = filename.replace(".json", "")
        all_filenames.append( generated_name )

    self.all_filenames = all_filenames
    return all_filenames

  def fetch_lwsm_presets(self, query=None):
    filtered_presets = []
    filenames = self.all_filenames
    for filename in filenames:
      if query.lower() in filename.lower():
        filtered_presets.append( filename )

    return filtered_presets


class KeywordQueryEventListener(EventListener):

  def on_event(self, event, extension):
    if event.get_argument() is None:
      presets = extension.set_lwsm_presets( extension.presets_path )
    else:
      presets = extension.fetch_lwsm_presets( event.get_argument() )

    items = []

    for preset in presets:
      items.append(
        ExtensionResultItem(
          icon='images/icon.png',
          name=preset,
          description='Restore lwsm preset %s' % preset,
          on_enter=RunScriptAction("lwsm restore %s" % preset, [])
        )
      )
    
    if len(items) <= 0 and len(extension.all_filenames) <= 0:
      items.append(
        ExtensionResultItem(
          icon='images/icon.png',
          name="No presets found in '%s'" % extension.presets_path
        )
      )

    return RenderResultListAction(items)

class PreferencesEventListener(EventListener):

  def on_event(self, event, extension):
    extension.set_presets_path( event.preferences['lwsm_location'] )

class PreferencesUpdateEventListener(EventListener):

  def on_event(self, event, extension):
    if event.id == 'lwsm_location':
      extension.set_presets_path( event.new_value )

if __name__ == '__main__':
  LwsmExtension().run()