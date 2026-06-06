#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

EXIT_OK = 0
EXIT_GENERAL_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_BLOCKED = 3
# Contrato congelado: un dry-run exitoso es exito real.
EXIT_DRY_RUN = EXIT_OK
EXIT_VERIFICATION_ROLLED_BACK = 5
EXIT_VERIFICATION_ROLLBACK_FAILED = 6
