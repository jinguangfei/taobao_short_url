from typing import Optional

import jwt
from fastapi import FastAPI, Depends, Query, Header, HTTPException, Request
from fastapi.routing import APIRoute
from tortoise.expressions import Q

from src.core.ctx import CTX_USER_ID, CTX_Q
from src.settings import settings