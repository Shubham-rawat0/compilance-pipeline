import json
import os
import logging
import re
from typing import Dict ,Any ,List
from langchain_openai import AzureChatOpenAI , AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import  SystemMessage, HumanMessage
from backend.src.graph.state import VideoAuditState , ComplianceIssue
from backend.src.services.video_indexer import VideoIndexerService
