/*
This file is part of jpcsp.

Jpcsp is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Jpcsp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Jpcsp.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <pspsdk.h>
#include <pspkernel.h>
#include <pspinit.h>
#include <psploadcore.h>
#include <psputilsforkernel.h>
#include <pspsysmem_kernel.h>
#include <psprtc.h>
#include <string.h>
#include "../common.h"

PSP_MODULE_INFO("JpcspTraceUser", PSP_MODULE_USER, 1, 0);

u64 syscallPlugin(u32 a0, u32 a1, u32 a2, u32 a3, u32 t0, u32 t1, u32 t2, u32 t3, SyscallInfo *syscallInfo, u32 ra, u32 sp, u32 gp) {
	u32 parameters[8];
	u64 result;
	int inOut = 0;

#if 0
if (syscallInfo->nid == 0x8EEFD953 && a3 == 443) {
  a2 = (u32) "http";
  a3 = 80;
} else if (syscallInfo->nid == 0xCDF8ECB9 && strncmp((char *) a1, "https", 5) == 0) {
  // Replace https with http
  strcpy((char *) a1 + 4, (char *) a1 + 5);
}
#endif

	parameters[0] = a0;
	parameters[1] = a1;
	parameters[2] = a2;
	parameters[3] = a3;
	parameters[4] = t0;
	parameters[5] = t1;
	parameters[6] = t2;
	parameters[7] = t3;

	commonInfo = syscallInfo->commonInfo;

	#if DEBUG_MUTEX
	mutexPreLog(syscallInfo, parameters);
	#endif

	if (syscallInfo->flags & FLAG_LOG_BEFORE_CALL) {
                if (syscallInfo->flags & FLAG_LOG_AFTER_CALL) {
                        // Display "IN" and "OUT" in front of syscall
                        // when it is logged both before and after.
                        inOut = 1;
                }

		syscallLog(syscallInfo, -inOut, parameters, 0, ra, sp, gp);

		if (syscallInfo->flags & FLAG_LOG_FLUSH_AFTER_CALL) {
			flushLogBuffer();
		}
	}

	if (syscallInfo->flags & FLAG_LOG_STACK_USAGE) {
		// Collect stackUsage information for user libraries
		prepareStackUsage(sp);
	}

	result = syscallInfo->originalEntry(a0, a1, a2, a3, t0, t1, t2, t3);

	if (syscallInfo->flags & FLAG_LOG_STACK_USAGE) {
		logStackUsage(syscallInfo);
	}

	if (syscallInfo->flags & FLAG_LOG_AFTER_CALL) {
		syscallLog(syscallInfo, inOut, parameters, result, ra, sp, gp);
	}

	if (syscallInfo->flags & FLAG_LOG_FLUSH_AFTER_CALL) {
		flushLogBuffer();
	}

	return result;
}

// Module Start
int module_start(SceSize args, void * argp) {
	return 0;
}

// Module Stop
int module_stop(SceSize args, void * argp) {
	openLogFile();

	printLog("JpcspTrace - module_stop\n");

	closeLogFile();

	return 0;
}
