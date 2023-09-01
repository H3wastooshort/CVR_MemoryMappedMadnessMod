//Lots of stuff here is stolen from SDraw. thanks

using ABI_RC.Core.Player;
using RootMotion.FinalIK;
using UnityEngine;
using MelonLoader;
namespace handOSC
{
    [DisallowMultipleComponent]
    class hand_mover : MonoBehaviour
    {
        public bool l_enabled = false;
        public bool r_enabled = false;

        VRIK m_vrIK = null;

        Vector3 l_hand_target_pos;
        Quaternion l_hand_target_rot;
        Vector3 r_hand_target_pos;
        Quaternion r_hand_target_rot;

        internal void OnAvatarClear()
        {
            m_vrIK = null;
        }

        internal void OnAvatarSetup()
        {
            m_vrIK = PlayerSetup.Instance._animator.GetComponent<VRIK>();
            m_vrIK.solver.OnPreUpdate += this.OnIKPreUpdate;
        }

        //what i actually did
        internal void OnIKPreUpdate()
        { if (l_enabled || r_enabled)
            {
                Vector3 pos = PlayerSetup.Instance.GetPlayerPosition();
                Quaternion rot = PlayerSetup.Instance.GetPlayerRotation();

                if (l_enabled)
                {
                    m_vrIK.solver.leftArm.IKPosition = (rot * l_hand_target_pos) + pos;
                    m_vrIK.solver.leftArm.IKRotation = l_hand_target_rot;
                    m_vrIK.solver.leftArm.bendGoalWeight = 0f;
                    m_vrIK.solver.leftArm.positionWeight = 1f;
                    m_vrIK.solver.leftArm.rotationWeight = 1f;
                }
                if (r_enabled)
                {
                    m_vrIK.solver.rightArm.IKPosition = (rot * r_hand_target_pos) + pos;
                    m_vrIK.solver.rightArm.IKRotation = r_hand_target_rot;
                    m_vrIK.solver.rightArm.bendGoalWeight = 0f;
                    m_vrIK.solver.rightArm.positionWeight = 1f;
                    m_vrIK.solver.rightArm.rotationWeight = 1f;
                }

                /*m_vrIK.solver.leftArm.target.position = (rot * l_hand_target_pos) + pos;
                m_vrIK.solver.leftArm.target.localRotation = l_hand_target_rot;
                m_vrIK.solver.rightArm.target.position = (rot * r_hand_target_pos) + pos;
                m_vrIK.solver.rightArm.target.localRotation = r_hand_target_rot;*/


                /*m_vrIK.solver.leftArm.shoulderRotationMode= IKSolverVR.Arm.ShoulderRotationMode.FromTo;
                m_vrIK.solver.rightArm.shoulderRotationMode = IKSolverVR.Arm.ShoulderRotationMode.FromTo;*/

            }
        }

        /*internal void set_hand(ref Transform target, Vector3 position, Vector3 rotation)
        {
            m_hips = PlayerSetup.Instance._animator.GetBoneTransform(HumanBodyBones.Hips);
            target.position = m_hips.position + position;
            target.eulerAngles = m_hips.eulerAngles + rotation;
        }*/

        public bool set_left_hand(Vector3 position, Quaternion rotation)
        {
            if (m_vrIK != null) {
                //set_hand(ref l_hand_target, position, rotation);
                l_hand_target_pos = position;
                l_hand_target_rot = rotation;
                return true;
            }
            else return false;
        }
        public bool set_right_hand(Vector3 position, Quaternion rotation)
        {
            if (m_vrIK != null) {
                //set_hand(ref r_hand_target, position, rotation);
                r_hand_target_pos = position;
                r_hand_target_rot = rotation;
                return true;
            }
            else return false;
        }

        public void dump_data(MelonLogger.Instance logger)
        {
            float conv = 360/(2*Mathf.PI);
            logger.Msg(string.Format("Left Target Pos: X{0} Y{1} Z{2}",l_hand_target_pos.x, l_hand_target_pos.y, l_hand_target_pos.z));
            logger.Msg(string.Format("Right Target Pos: X{0} Y{1} Z{2}", r_hand_target_pos.x, r_hand_target_pos.y, r_hand_target_pos.z));
            logger.Msg(string.Format("Left Target Rot: X{0} Y{1} Z{2}", l_hand_target_rot.eulerAngles.x*conv, l_hand_target_rot.eulerAngles.y*conv, l_hand_target_rot.eulerAngles.z * conv));
            logger.Msg(string.Format("Right Target Rot: X{0} Y{1} Z{2}", r_hand_target_rot.eulerAngles.x*conv, r_hand_target_rot.eulerAngles.y*conv, r_hand_target_rot.eulerAngles.z * conv));
        }
    }
}
