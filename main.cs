﻿using ABI_RC.Core.Player;
using ABI_RC.Systems.InputManagement;
using handOSC;
using MelonLoader;
using System.Reflection;
using UnityEngine;
using HarmonyLib;


namespace handsOSC
{
    public class handsOSC_mod : MelonMod
    {
        static hand_mover hm = new hand_mover();

        MemoryMapReader l_mapReader = null;
        MemoryMapReader r_mapReader = null;
        MemoryMapReader ctrl_mapReader = null;
        byte[] l_buffer = null;
        byte[] r_buffer = null;
        byte[] ctrl_buffer = null;

        static input_stuff in_stuff = new input_stuff();

        public override void OnInitializeMelon()
        {
            LoggerInstance.Msg("memory-mapped madness by H3");

            l_mapReader = new MemoryMapReader();
            l_buffer = new byte[1024];
            r_mapReader = new MemoryMapReader();
            r_buffer = new byte[1024];
            ctrl_mapReader = new MemoryMapReader();
            ctrl_buffer = new byte[1024];

            l_mapReader.Open("hand/left");
            r_mapReader.Open("hand/right");
            ctrl_mapReader.Open("ctrl");


            HarmonyInstance.Patch(
                typeof(PlayerSetup).GetMethod(nameof(PlayerSetup.ClearAvatar)),
                null,
                new HarmonyMethod(typeof(handsOSC_mod).GetMethod(nameof(handsOSC_mod.OnAvatarClear), BindingFlags.Static | BindingFlags.NonPublic))
            );
            HarmonyInstance.Patch(
                typeof(PlayerSetup).GetMethod(nameof(PlayerSetup.SetupAvatar)),
                null,
                new HarmonyMethod(typeof(handsOSC_mod).GetMethod(nameof(handsOSC_mod.OnAvatarSetup), BindingFlags.Static | BindingFlags.NonPublic))
            );
        }

             static void OnAvatarSetup()
        {
            hm.OnAvatarSetup();
        }

        static void OnAvatarClear()
        {
            hm.OnAvatarClear();
        }


        Vector3 dat_to_pos(hand_data hand)
        {
            return new Vector3(hand.handPositionX, hand.handPositionY, hand.handPositionZ);
        }

        Quaternion dat_to_rot(hand_data hand)
        {
            return new Quaternion
            {
                eulerAngles = new Vector3(hand.handRotationX, hand.handRotationY, hand.handRotationZ)
            };
        }

        public override void OnUpdate()
        {
            if (l_mapReader.Read(ref l_buffer))
            {
                hand_data l_hand = hand_data_func.ToObject(l_buffer);
                hm.set_left_hand(dat_to_pos(l_hand), dat_to_rot(l_hand));
            }
            if (r_mapReader.Read(ref r_buffer))
            {
                hand_data r_hand = hand_data_func.ToObject(r_buffer);
                hm.set_right_hand(dat_to_pos(r_hand), dat_to_rot(r_hand));
            }
            if (in_stuff.use_ctrl)
                if(ctrl_mapReader.Read(ref ctrl_buffer))
                {
                    ctrl_data ctrl = ctrl_data_func.ToObject(ctrl_buffer);
                    in_stuff.update_ctrl(ctrl);
                }
        }

        public override void OnDeinitializeMelon()
        {
            l_mapReader?.Close();
            l_mapReader = null;
            l_buffer = null;
            r_mapReader?.Close();
            r_mapReader = null;
            r_buffer = null;
        }

        /*static Vector3 l_hand_pos = new Vector3(0, 0, 0);
        static Vector3 r_hand_pos = new Vector3(0, 0, 0);
        void setHands()
        {
            hm.set_left_hand(l_hand_pos, Quaternion.identity);
            hm.set_right_hand(r_hand_pos, Quaternion.identity);
        }

        float move_amount = 0.05f;*/
        public override void OnLateUpdate()
        {
            /*
            if (Input.GetKeyDown(KeyCode.PageUp)) { move_amount = 0.5f; }
            if (Input.GetKeyDown(KeyCode.PageDown)) { move_amount = 0.05f; }
            
            if (Input.GetKeyDown(KeyCode.F1)) {l_hand_pos.x += move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F2)) {l_hand_pos.x -= move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F3)) {l_hand_pos.y += move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F4)) {l_hand_pos.y -= move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F5)) {l_hand_pos.z += move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F6)) {l_hand_pos.z -= move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F7)) {r_hand_pos.x += move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F8)) {r_hand_pos.x -= move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F9)) {r_hand_pos.y += move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F10)) {r_hand_pos.y -= move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F11)) {r_hand_pos.z += move_amount; setHands(); }
            if (Input.GetKeyDown(KeyCode.F12)) {r_hand_pos.z -= move_amount; setHands(); }
            */

            if (Input.GetKeyDown(KeyCode.F1))
            {
                hm.l_enabled = !hm.l_enabled;
                LoggerInstance.Msg(hm.l_enabled ? "Left Enabled" : "Left Disabled"); 
            }
            if (Input.GetKeyDown(KeyCode.F2))
            {
                hm.r_enabled = !hm.r_enabled;
                LoggerInstance.Msg(hm.r_enabled ? "Right Enabled" : "Right Disabled");
            }
            if (Input.GetKeyDown(KeyCode.F3))
            {
                in_stuff.use_ctrl = !in_stuff.use_ctrl;
                LoggerInstance.Msg(in_stuff.use_ctrl ? "Control Enabled" : "Control Disabled");
            }
            if (Input.GetKeyDown(KeyCode.F4))
            {
                hm.dump_data(LoggerInstance);
            }
        }

        //kinda stolen from kafeijao
        [HarmonyPatch]
        internal class HarmonyPatches
        {

            [HarmonyPostfix]
            [HarmonyPatch(typeof(CVRInputManager), "Start"/*nameof(CVRInputManager.Start)*/)]
            public static void After_CVRInputManager_Start(CVRInputManager __instance)
            {
                __instance.AddInputModule(in_stuff);
            }
        }
    }
}
