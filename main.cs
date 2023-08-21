using ABI_RC.Core.Player;
using handOSC;
using MelonLoader;
using System;
using System.Reflection;
using UnityEngine;

namespace handsOSC
{
    public class handsOSC_mod : MelonMod
    {
        static hand_mover hm = new hand_mover();

        MemoryMapReader l_mapReader = null;
        MemoryMapReader r_mapReader = null;
        byte[] l_buffer = null;
        byte[] r_buffer = null;

        public override void OnInitializeMelon()
        {
            LoggerInstance.Msg("HandsOSC by H3");

            l_mapReader = new MemoryMapReader();
            l_buffer = new byte[1024];
            r_mapReader = new MemoryMapReader();
            r_buffer = new byte[1024];

            l_mapReader.Open("hand/left");
            r_mapReader.Open("hand/right");

            HarmonyInstance.Patch(
                typeof(PlayerSetup).GetMethod(nameof(PlayerSetup.ClearAvatar)),
                null,
                new HarmonyLib.HarmonyMethod(typeof(handsOSC_mod).GetMethod(nameof(handsOSC_mod.OnAvatarClear), BindingFlags.Static | BindingFlags.NonPublic))
            );
            HarmonyInstance.Patch(
                typeof(PlayerSetup).GetMethod(nameof(PlayerSetup.SetupAvatar)),
                null,
                new HarmonyLib.HarmonyMethod(typeof(handsOSC_mod).GetMethod(nameof(handsOSC_mod.OnAvatarSetup), BindingFlags.Static | BindingFlags.NonPublic))
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
            return new Quaternion(hand.handRotationX, hand.handRotationY, hand.handRotationZ, hand.handRotationW);
        }

        public override void OnUpdate()
        {
            /*if (l_mapReader.Read(ref l_buffer))
            {
                hand_data l_hand = hand_data.ToObject(l_buffer);
                hm.set_left_hand(dat_to_pos(l_hand), dat_to_rot(l_hand));
            }
            if (r_mapReader.Read(ref r_buffer))
            {
                hand_data r_hand = hand_data.ToObject(r_buffer);
                hm.set_left_hand(dat_to_pos(r_hand), dat_to_rot(r_hand));
            }*/
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

        static Vector3 l_hand_pos = new Vector3(0, 0, 0);
        static Vector3 r_hand_pos = new Vector3(0, 0, 0);
        void setHands()
        {
            hm.set_left_hand(l_hand_pos, Quaternion.identity);
            hm.set_right_hand(r_hand_pos, Quaternion.identity);
        }

        float move_amount = 0.05f;
        public override void OnLateUpdate()
        {
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

            
        }
    }
}
