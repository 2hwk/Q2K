#define KEYMAP(                                                 \
                                                                \
         k01, k02, k03, k04, k05, k06,                        k09, k0a, k0b, k0c, k0d, k0e,      \
    k10, k11, k12, k13, k14, k15, k16,                        k19, k1a, k1b, k1c, k1d, k1e, k1f, \
    k20, k21, k22, k23, k24, k25, k26,                        k29, k2a, k2b, k2c, k2d, k2e, k2f, \
    k30, k31, k32, k33, k34, k35, k36,                        k39, k3a, k3b, k3c, k3d, k3e, k3f, \
    k40, k41, k42, k43, k44, k45, k46, k47, k37,    k38, k48, k49, k4a, k4b, k4c, k4d, k4e, k4f, \
    k50, k51, k52, k53, k54, k55, k56,   k57,          k58,   k59, k5a, k5b, k5c, k5d, k5e, k5f, \
    \
    PL1, PL2, PL3, \
    PR1, PR2, PR3 \
    )                                             \
                                                  \
   /* matrix positions, inverted left and right for I2C to be on row 0-7 */\
   {                                              \
                                                  \
    { k5f,   k4f,   k3f,  k2f,   k1f,   KC_NO},   \
    { k5e,   k4e,   k3e,  k2e,   k1e,   k0e  },   \
    { k5d,   k4d,   k3d,  k2d,   k1d,   k0d  },   \
    { k5c,   k4c,   k3c,  k2c,   k1c,   k0c  },   \
    { k5b,   k4b,   k3b,  k2b,   k1b,   k0b  },   \
    { k5a,   k4a,   k3a,  k2a,   k1a,   k0a  },   \
    { k59,   k49,   k39,  k29,   k19,   k09  },   \
    { k58,   k48,   k38,  PR1,   PR2,   PR3   },   \
    \
    { k57,   k47,  k37,   PL1,   PL2,   PL3   },   \
    { k56,   k46,  k36,   k26,   k16,   k06   },   \
    { k55,   k45,  k35,   k25,   k15,   k05   },   \
    { k54,   k44,  k34,   k24,   k14,   k04   },   \
    { k53,   k43,  k33,   k23,   k13,   k03   },   \
    { k52,   k42,  k32,   k22,   k12,   k02   },   \
    { k51,   k41,  k31,   k21,   k11,   k01   },   \
    { k50,   k40,  k30,   k20,   k10,   KC_NO }   \
   }
