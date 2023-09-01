using ABI_RC.Core.UI;
using System;
using System.IO.MemoryMappedFiles;
using System.IO;
using UnityEngine;
using System.Runtime.InteropServices;

struct hand_data
{
    public float handPositionX;
    public float handPositionY;
    public float handPositionZ;

    public float handRotationX;
    public float handRotationY;
    public float handRotationZ;
    public float handRotationW;
}

class hand_data_func { 
static public byte[] ToBytes(hand_data p_handData)
{
    int l_size = Marshal.SizeOf(p_handData);
    byte[] l_arr = new byte[l_size];

    IntPtr ptr = Marshal.AllocHGlobal(l_size);
    Marshal.StructureToPtr(p_handData, ptr, true);
    Marshal.Copy(ptr, l_arr, 0, l_size);
    Marshal.FreeHGlobal(ptr);
    return l_arr;
}

static public hand_data ToObject(byte[] p_buffer)
{
    hand_data l_handData = new hand_data();

    int l_size = Marshal.SizeOf(l_handData);
    IntPtr l_ptr = Marshal.AllocHGlobal(l_size);

    Marshal.Copy(p_buffer, 0, l_ptr, l_size);

    l_handData = (hand_data)Marshal.PtrToStructure(l_ptr, l_handData.GetType());
    Marshal.FreeHGlobal(l_ptr);

    return l_handData;
}
}

struct ctrl_data
{
    public float emoteL;
    public float emoteR;
    public float moveX;
    public float moveY;
}

class ctrl_data_func
{
    static public byte[] ToBytes(ctrl_data p_handData)
    {
        int l_size = Marshal.SizeOf(p_handData);
        byte[] l_arr = new byte[l_size];

        IntPtr ptr = Marshal.AllocHGlobal(l_size);
        Marshal.StructureToPtr(p_handData, ptr, true);
        Marshal.Copy(ptr, l_arr, 0, l_size);
        Marshal.FreeHGlobal(ptr);
        return l_arr;
    }

    static public ctrl_data ToObject(byte[] p_buffer)
    {
        ctrl_data l_handData = new ctrl_data();

        int l_size = Marshal.SizeOf(l_handData);
        IntPtr l_ptr = Marshal.AllocHGlobal(l_size);

        Marshal.Copy(p_buffer, 0, l_ptr, l_size);

        l_handData = (ctrl_data)Marshal.PtrToStructure(l_ptr, l_handData.GetType());
        Marshal.FreeHGlobal(l_ptr);

        return l_handData;
    }
}

namespace handOSC
{    static class Utils
    {
        public static Matrix4x4 GetMatrix(this Transform p_transform, bool p_pos = true, bool p_rot = true, bool p_scl = false)
        {
            return Matrix4x4.TRS(p_pos ? p_transform.position : Vector3.zero, p_rot ? p_transform.rotation : Quaternion.identity, p_scl ? p_transform.lossyScale : Vector3.one);
        }

        public static void ShowHUDNotification(string p_title, string p_message, string p_small = "", bool p_immediate = false)
        {
            if (CohtmlHud.Instance != null)
            {
                if (p_immediate)
                    CohtmlHud.Instance.ViewDropTextImmediate(p_title, p_message, p_small);
                else
                    CohtmlHud.Instance.ViewDropText(p_title, p_message, p_small);
            }
        }

        public static void Swap<T>(ref T lhs, ref T rhs)
        {
            T temp = lhs;
            lhs = rhs;
            rhs = temp;
        }
    }
}

    class MemoryMapReader
    {
        MemoryMappedFile m_file = null;
        MemoryMappedViewStream m_stream = null;
        int m_dataSize = 0;

        public bool Open(string p_path, int p_dataSize = 1024)
        {
            if (m_file == null)
            {
                m_dataSize = p_dataSize;

                m_file = MemoryMappedFile.CreateOrOpen(p_path, m_dataSize, MemoryMappedFileAccess.ReadWrite);
                m_stream = m_file.CreateViewStream(0, m_dataSize, MemoryMappedFileAccess.Read);
            }
            return (m_file != null);
        }

        public bool Read(ref byte[] p_data)
        {
            bool l_result = false;
            if ((m_stream != null) && m_stream.CanRead)
            {
                try
                {
                    m_stream.Seek(0, SeekOrigin.Begin);
                    m_stream.Read(p_data, 0, (p_data.Length > m_dataSize) ? m_dataSize : p_data.Length);
                    l_result = true;
                }
                catch (System.Exception) { }
            }
            return l_result;
        }

        public void Close()
        {
            if (m_file != null)
            {
                m_stream.Close();
                m_stream.Dispose();
                m_stream = null;

                m_file.Dispose();
                m_file = null;

                m_dataSize = 0;
            }
        }
    }
