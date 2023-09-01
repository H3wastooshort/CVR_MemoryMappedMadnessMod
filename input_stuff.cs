using ABI_RC.Systems.InputManagement;
using UnityEngine;

namespace handOSC
{
    internal class input_stuff : CVRInputModule
    {
        private CVRInputManager input_man;
        public bool use_ctrl = false;
        ctrl_data ctrl;
        public void update_ctrl(ctrl_data new_ctrl)
        {
            ctrl=new_ctrl;
        }
        public override void ModuleAdded()
        {
            input_man = CVRInputManager.Instance;
        }
        public override void Update_Always()
        {
            if (use_ctrl)
            {
                //input_man.emote = ctrl.emoteR;
                input_man.gestureLeft = ctrl.emoteL;
                input_man.gestureRight = ctrl.emoteR;
                input_man.movementVector += new Vector3(ctrl.moveX, 0.0f, ctrl.moveY);
                input_man.accelerate += Mathf.Clamp(ctrl.moveY, -1f, 1f);
                input_man.brake += Mathf.Clamp01(ctrl.moveY * -1f);
            }
        }
    }
}
