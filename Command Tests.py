#Author-Justin K
#Description-Testing command stuff

import adsk.core, adsk.fusion, adsk.cam, traceback
import json

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []
heightScale = None

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        # buttonSample = cmdDefs.addButtonDefinition('VFLSetAttributes', 
        #                                            'Modify VEX Part', 
        #                                            'Modify parametric parts from the VEX Fusion 360 Library')
        buttonSample = cmdDefs.addButtonDefinition('VFLSetAttributes', 
                                                   'Set Custom Attributes', 
                                                   'Set custom Attributes for parametric parts from the VEX Fusion 360 Library.\n\nSelect part component and input valid JSON string.',
                                                   './resources/button')
        # buttonSample = cmdDefs.addButtonDefinition('VFLSetAttributes', 
        #                                            'Python Sample Button', 
        #                                            'Sample button tooltip',
        #                                            './resources/button')
        
        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        modifyPanel = ui.allToolbarPanels.itemById('SolidModifyPanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = modifyPanel.controls.addCommand(buttonSample)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        
        # Get the command
        cmd = eventArgs.command

        # Get the CommandInputs collection to create new command inputs.            
        inputs = cmd.commandInputs


        # Create the slider to get the base length, setting the range of the slider to 
        # be 1 to 10 of whatever the current document unit is. 
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        # minVal = des.unitsManager.convert(1, des.unitsManager.defaultLengthUnits, 'cm' )
        # maxVal = des.unitsManager.convert(10, des.unitsManager.defaultLengthUnits, 'cm' )
        # baseLength = inputs.addFloatSliderCommandInput('baseLength', 
        #                                                'Base Length', 
        #                                                des.unitsManager.defaultLengthUnits,
        #                                                minVal, maxVal, False)

        # Create a check box to get if it should be an equilateral triangle or not.
        # equilateral = inputs.addBoolValueInput('equilateral', 'Equilateral', 
        #                                        True, '', False)
        # Create the value input to get the height scale. 
        # global heightScale
        # heightScale = inputs.addValueInput('heightScale', 'Height Scale', 
        #                                    '', adsk.core.ValueInput.createByReal(0.75))

        selectionInput = cmd.commandInputs.addSelectionInput("selection", "Select Parametric Part", "Component to select")
        selectionInput.setSelectionLimits(1, 0)
        selectionInput.addSelectionFilter("Occurrences")
        textBox = cmd.commandInputs.addStringValueInput('textBox', 'JSON String')

        # Connect to the execute event.
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


# Event handler for the execute event.
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            
            # Get the command
            cmd = eventArgs.command

            # Get the CommandInputs collection to create new command inputs.            
            inputs = cmd.commandInputs

            # Code to react to the event.
            app = adsk.core.Application.get()
            ui  = app.userInterface

            selectionInput = inputs.itemById("selection")
            selectedComp = selectionInput.selection(0).entity.component

            jsonString = inputs.itemById("textBox").value

            try:
                json.loads(jsonString)
                selectedComp.attributes.add("VFL", "partData", jsonString)
                appliedAttributes = selectedComp.attributes.itemByName("VFL", "partData").value
                ui.messageBox(appliedAttributes + '\n\nWas applied successfully.')
            except:
                ui.messageBox(jsonString + '\n\nis not a valid JSON string.', 'Invalid entry', 
                              adsk.core.MessageBoxButtonTypes.OKButtonType, 
                              adsk.core.MessageBoxIconTypes.CriticalIconType)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('VFLSetAttributes')
        if cmdDef:
            cmdDef.deleteMe()
            
        modifyPanel = ui.allToolbarPanels.itemById('SolidModifyPanel')
        cntrl = modifyPanel.controls.itemById('VFLSetAttributes')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))