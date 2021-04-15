# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for an assistant that schedules reminders and
# reacts to external events.

from typing import Any, Text, Dict, List
import datetime
import asyncio

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ReminderScheduled, ReminderCancelled
from rasa_sdk.executor import CollectingDispatcher


class ActionSetReminder(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("I will remind you in 5 seconds.")

        date = datetime.datetime.now() + datetime.timedelta(seconds=5)
        entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            entities=entities,
            name="my_reminder",
            kill_on_user_message=False,
        )

        return [reminder]


class ActionReactToReminder(Action):
    """Reminds the user to call someone."""

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        name = next(tracker.get_slot("PERSON"), "someone")
        dispatcher.utter_message(f"Remember to call {name}!")

        return []

class ActionSendMessage(Action):
    """ sends a message"""

    def name(self)-> Text:
        return "action_send_msg"
    
    def ext_event(self,cid=None): 
        #async with aiohttp.ClientSession as session:
            import requests
            import json
            import time
            time.sleep(5)
            headers = {'Content-Type': 'application/json',}
            params = (('output_channel', 'latest'),)
            url="http://rasa-x:5002/conversations/"+cid+"/trigger_intent"
            d = {"name" : "EXTERNAL_dry_plant", "entities": {"plant": "Orchid"}}
            print(url,d)
            try:
                x=requests.post(url, headers=headers, params=params,data=json.dumps(d),timeout=1)
            except requests.Timeout:
                pass

            # async with session.post(url=url,data=d,headers=headers) as resp:
            #     return await resp.text()
                

    async def main(self,cid=None):
        asyncio.create_task(self.ext_event(cid=cid))
        return

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict[Text, Any]]:    
        import multiprocessing as mp
        cid=tracker.sender_id
        t=mp.Process(target=self.ext_event,args=(cid,))
        t.start()
        
        #c="curl -H 'Content-type':'application/json' -XPOST -d '"+d+"' "+url+"?output_channel=latest"
        #os.system(c)
         
        #x=requests.request("POST", url, headers=headers, params=params,data=json.dumps(d))
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url,data=json.dumps(d)) as resp:
        #         #print(resp.status)
        #         #print(await resp.text())
        #         #print(f'url={x.url} data={x.content}')
        
        return[]
    
class ActionDummy(Action):
    """this clears the error"""
    
    def name(self)->Text:
        return "action_dummy"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        return []





class ActionTellID(Action):
    """Informs the user about the conversation ID."""

    def name(self) -> Text:
        return "action_tell_id"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id

        dispatcher.utter_message(f"The ID of this conversation is '{conversation_id}'.")
        dispatcher.utter_message(
            f"Trigger an intent with: \n"
            f'curl -H "Content-Type: application/json" '
            f'-X POST -d \'{{"name": "EXTERNAL_dry_plant", '
            f'"entities": {{"plant": "Orchid"}}}}\' '
            f'"http://localhost:5005/conversations/{conversation_id}'
            f'/trigger_intent?output_channel=latest"'
        )

        return []


class ActionWarnDry(Action):
    """Informs the user that a plant needs water."""

    def name(self) -> Text:
        return "action_warn_dry"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # print("in action_warn_dry run")
        # for k,v in tracker.current_state().items():
        #     print(k,v)
        plant = next(tracker.get_latest_entity_values("plant"))
        # print(type(plant))
        # #p=next(plant)
        print("flower={}".format(plant))
        # #print("entity=".format(plant))
        # dispatcher.utter_message(response="utter_plant_warn")
        dispatcher.utter_message(f"Your {plant} needs some water!")

        return []


class ForgetReminders(Action):
    """Cancels all reminders."""

    def name(self) -> Text:
        return "action_forget_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Okay, I'll cancel all your reminders.")

        # Cancel all reminders
        return [ReminderCancelled()]
