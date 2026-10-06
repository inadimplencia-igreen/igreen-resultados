import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
import base64
import re
import io
import warnings
warnings.filterwarnings('ignore')

import base64 as _b64
_HTML_B64 = "cyBzdAppbXBvcnQgcGFuZGFzIGFzIHBkCmZyb20gcHltb25nbyBpbXBvcnQgTW9uZ29DbGllbnQKZnJvbSBkYXRldGltZSBpbXBvcnQgZGF0ZXRpbWUsIGRhdGUKaW1wb3J0IGJhc2U2NAppbXBvcnQgcmUKaW1wb3J0IGlvCmltcG9ydCB3YXJuaW5ncwp3YXJuaW5ncy5maWx0ZXJ3YXJuaW5ncygnaWdub3JlJykKCnN0LnNldF9wYWdlX2NvbmZpZygKICAgIHBhZ2VfdGl0bGU9ImlHcmVlbiBNb25pdG9yaWFzIiwKICAgIHBhZ2VfaWNvbj0i8J+MvyIsCiAgICBsYXlvdXQ9IndpZGUiLAogICAgaW5pdGlhbF9zaWRlYmFyX3N0YXRlPSJleHBhbmRlZCIKKQoKc3QubWFya2Rvd24oIiIiCjxzdHlsZT4KQGltcG9ydCB1cmwoJ2h0dHBzOi8vZm9udHMuZ29vZ2xlYXBpcy5jb20vY3NzMj9mYW1pbHk9SW50ZXI6d2dodEAzMDA7NDAwOzUwMDs2MDA7NzAwOzgwMCZkaXNwbGF5PXN3YXAnKTsKKiB7IGZvbnQtZmFtaWx5OiAnSW50ZXInLCBzYW5zLXNlcmlmICFpbXBvcnRhbnQ7IH0KLnN0QXBwIHsgYmFja2dyb3VuZC1jb2xvcjogI2YwZjdmMCAhaW1wb3J0YW50OyB9CltkYXRhLXRlc3RpZD0ic3RTaWRlYmFyIl0geyBiYWNrZ3JvdW5kOiAjZjVmYmY1ICFpbXBvcnRhbnQ7IGJvcmRlci1yaWdodDogMXB4IHNvbGlkICNkMGU4ZDAgIWltcG9ydGFudDsgfQpbZGF0YS10ZXN0aWQ9InN0U2lkZWJhciJdIC5zdFJhZGlvID4gZGl2ID4gcCB7IGRpc3BsYXk6IG5vbmUgIWltcG9ydGFudDsgfQpbZGF0YS10ZXN0aWQ9InN0U2lkZWJhciJdIC5zdFJhZGlvIGxhYmVsIHsKICAgIGNvbG9yOiAjMmQ0YTJkICFpbXBvcnRhbnQ7IGZvbnQtc2l6ZTogMTNweCAhaW1wb3J0YW50OyBmb250LXdlaWdodDogNTAwICFpbXBvcnRhbnQ7CiAgICBwYWRkaW5nOiAxMHB4IDE2cHggIWltcG9ydGFudDsgZGlzcGxheTogZmxleCAhaW1wb3J0YW50OyBhbGlnbi1pdGVtczogY2VudGVyICFpbXBvcnRhbnQ7CiAgICBib3JkZXItcmFkaXVzOiA4cHggIWltcG9ydGFudDsgbWFyZ2luOiAxcHggMCAhaW1wb3J0YW50OyB3aWR0aDogMTAwJSAhaW1wb3J0YW50OwogICAgYmFja2dyb3VuZDogI2ZmZmZmZiAhaW1wb3J0YW50OyBib3JkZXI6IDFweCBzb2xpZCAjZDhlYWQ4ICFpbXBvcnRhbnQ7CiAgICBtaW4taGVpZ2h0OiA0MHB4ICFpbXBvcnRhbnQ7IHRyYW5zaXRpb246IGFsbCAwLjE1cyAhaW1wb3J0YW50Owp9CltkYXRhLXRlc3RpZD0ic3RTaWRlYmFyIl0gLnN0UmFkaW8gbGFiZWw6aG92ZXIgeyBiYWNrZ3JvdW5kOiAjZWRmN2VkICFpbXBvcnRhbnQ7IGJvcmRlci1jb2xvcjogIzJlN2QzMiAhaW1wb3J0YW50OyB9CltkYXRhLXRlc3RpZD0ic3RTaWRlYmFyIl0gLnN0UmFkaW8gW2RhdGEtYmFzZXdlYj0icmFkaW8iXSA+IGRpdjpmaXJzdC1jaGlsZCB7IGRpc3BsYXk6IG5vbmUgIWltcG9ydGFudDsgfQpbZGF0YS10ZXN0aWQ9InN0U2lkZWJhciJdIC5zdFJhZGlvIGxhYmVsW2RhdGEtY2hlY2tlZD0idHJ1ZSJdIHsKICAgIGNvbG9yOiAjZmZmZmZmICFpbXBvcnRhbnQ7IGJhY2tncm91bmQ6ICMyZTdkMzIgIWltcG9ydGFudDsgYm9yZGVyLWNvbG9yOiAjMmU3ZDMyICFpbXBvcnRhbnQ7IGZvbnQtd2VpZ2h0OiA2MDAgIWltcG9ydGFudDsKfQpbZGF0YS10ZXN0aWQ9InN0TWV0cmljIl0geyBiYWNrZ3JvdW5kOiAjZmZmZmZmICFpbXBvcnRhbnQ7IGJvcmRlcjogMXB4IHNvbGlkICNlMGU4ZTAgIWltcG9ydGFudDsgYm9yZGVyLXJhZGl1czogMTBweCAhaW1wb3J0YW50OyBwYWRkaW5nOiAxNnB4IDIwcHggIWltcG9ydGFudDsgYm9yZGVyLXRvcDogM3B4IHNvbGlkICMyZTdkMzIgIWltcG9ydGFudDsgfQpbZGF0YS10ZXN0aWQ9InN0TWV0cmljVmFsdWUiXSB7IGNvbG9yOiAjMWEyZTFhICFpbXBvcnRhbnQ7IGZvbnQtc2l6ZTogMTZweCAhaW1wb3J0YW50OyBmb250LXdlaWdodDogNzAwICFpbXBvcnRhbnQ7IH0KW2RhdGEtdGVzdGlkPSJzdE1ldHJpY0xhYmVsIl0geyBjb2xvcjogIzVhOGE1YSAhaW1wb3J0YW50OyBmb250LXNpemU6IDEwcHggIWltcG9ydGFudDsgdGV4dC10cmFuc2Zvcm06IHVwcGVyY2FzZTsgbGV0dGVyLXNwYWNpbmc6IDEuNXB4OyBmb250LXdlaWdodDogNjAwOyB9Ci5zdEJ1dHRvbiA+IGJ1dHRvbiB7IGJhY2tncm91bmQ6ICNmMGY3ZjAgIWltcG9ydGFudDsgY29sb3I6ICMyZTdkMzIgIWltcG9ydGFudDsgYm9yZGVyOiAxcHggc29saWQgI2M4ZTBjOCAhaW1wb3J0YW50OyBib3JkZXItcmFkaXVzOiA2cHggIWltcG9ydGFudDsgZm9udC13ZWlnaHQ6IDUwMCAhaW1wb3J0YW50OyBmb250LXNpemU6IDEycHggIWltcG9ydGFudDsgfQouc3RCdXR0b24gPiBidXR0b246aG92ZXIgeyBiYWNrZ3JvdW5kOiAjMmU3ZDMyICFpbXBvcnRhbnQ7IGNvbG9yOiAjZmZmZmZmICFpbXBvcnRhbnQ7IH0KaDEgeyBjb2xvcjogIzFhMmUxYSAhaW1wb3J0YW50OyBmb250LXNpemU6IDIwcHggIWltcG9ydGFudDsgZm9udC13ZWlnaHQ6IDcwMCAhaW1wb3J0YW50OyB9CmgyIHsgY29sb3I6ICMyZDRhMmQgIWltcG9ydGFudDsgZm9udC1zaXplOiAxNnB4ICFpbXBvcnRhbnQ7IGZvbnQtd2VpZ2h0OiA2MDAgIWltcG9ydGFudDsgfQpwIHsgY29sb3I6ICMxYTNhMWEgIWltcG9ydGFudDsgZm9udC1zaXplOiAxM3B4OyB9CmhyIHsgYm9yZGVyOiBub25lICFpbXBvcnRhbnQ7IGJvcmRlci10b3A6IDFweCBzb2xpZCAjZTBlOGUwICFpbXBvcnRhbnQ7IG1hcmdpbjogMTRweCAwICFpbXBvcnRhbnQ7IH0KLnN0VGV4dElucHV0IGlucHV0LCAuc3ROdW1iZXJJbnB1dCBpbnB1dCwgLnN0VGV4dEFyZWEgdGV4dGFyZWEgeyBiYWNrZ3JvdW5kOiAjZmZmZmZmICFpbXBvcnRhbnQ7IGJvcmRlcjogMXB4IHNvbGlkICNjOGUwYzggIWltcG9ydGFudDsgY29sb3I6ICMxYTJlMWEgIWltcG9ydGFudDsgYm9yZGVyLXJhZGl1czogOHB4ICFpbXBvcnRhbnQ7IGZvbnQtc2l6ZTogMTNweCAhaW1wb3J0YW50OyB9Ci5zdFNlbGVjdGJveCA+IGRpdiA+IGRpdiB7IGJhY2tncm91bmQ6ICNmZmZmZmYgIWltcG9ydGFudDsgYm9yZGVyOiAxcHggc29saWQgI2M4ZTBjOCAhaW1wb3J0YW50OyBjb2xvcjogIzFhMmUxYSAhaW1wb3J0YW50OyBib3JkZXItcmFkaXVzOiA4cHggIWltcG9ydGFudDsgfQouc3RUYWJzIFtkYXRhLWJhc2V3ZWI9InRhYi1saXN0Il0geyBiYWNrZ3JvdW5kOiAjZjBmN2YwICFpbXBvcnRhbnQ7IGJvcmRlci1yYWRpdXM6IDhweCAhaW1wb3J0YW50OyBwYWRkaW5nOiA0cHggIWltcG9ydGFudDsgYm9yZGVyOiAxcHggc29saWQgI2M4ZTBjOCAhaW1wb3J0YW50OyB9Ci5zdFRhYnMgW2RhdGEtYmFzZXdlYj0idGFiIl0geyBjb2xvcjogIzVhOGE1YSAhaW1wb3J0YW50OyBib3JkZXItcmFkaXVzOiA2cHggIWltcG9ydGFudDsgZm9udC1zaXplOiAxMnB4ICFpbXBvcnRhbnQ7IH0KLnN0VGFicyBbYXJpYS1zZWxlY3RlZD0idHJ1ZSJdIHsgYmFja2dyb3VuZDogIzJlN2QzMiAhaW1wb3J0YW50OyBjb2xvcjogI2ZmZmZmZiAhaW1wb3J0YW50OyB9Ci5zdFN1Y2Nlc3MgPiBkaXYgeyBiYWNrZ3JvdW5kOiAjZjBmYWYwICFpbXBvcnRhbnQ7IGJvcmRlci1sZWZ0OiAzcHggc29saWQgIzJlN2QzMiAhaW1wb3J0YW50OyBjb2xvcjogIzJlN2QzMiAhaW1wb3J0YW50OyBib3JkZXItcmFkaXVzOiA4cHggIWltcG9ydGFudDsgfQouc3RFcnJvciA+IGRpdiB7IGJhY2tncm91bmQ6ICNmZmY1ZjUgIWltcG9ydGFudDsgYm9yZGVyLWxlZnQ6IDNweCBzb2xpZCAjYzYyODI4ICFpbXBvcnRhbnQ7IGNvbG9yOiAjYzYyODI4ICFpbXBvcnRhbnQ7IGJvcmRlci1yYWRpdXM6IDhweCAhaW1wb3J0YW50OyB9Ci5zdFdhcm5pbmcgPiBkaXYgeyBiYWNrZ3JvdW5kOiAjZmZmYmYwICFpbXBvcnRhbnQ7IGJvcmRlci1sZWZ0OiAzcHggc29saWQgI2YwYzAwMCAhaW1wb3J0YW50OyBjb2xvcjogIzhhNmEwMCAhaW1wb3J0YW50OyBib3JkZXItcmFkaXVzOiA4cHggIWltcG9ydGFudDsgfQpbZGF0YS10ZXN0aWQ9InN0U2lkZWJhckNvbGxhcHNlQnV0dG9uIl0geyBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7IH0KW2RhdGEtdGVzdGlkPSJjb2xsYXBzZWRDb250cm9sIl0geyBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7IH0KW2RhdGEtdGVzdGlkPSJzdFNpZGViYXJDb2xsYXBzZWRDb250cm9sIl0geyBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7IH0KYnV0dG9uW2RhdGEtdGVzdGlkPSJiYXNlQnV0dG9uLWhlYWRlciJdIHsgZGlzcGxheTogbm9uZSAhaW1wb3J0YW50OyB9CiNNYWluTWVudSB7IHZpc2liaWxpdHk6IGhpZGRlbiAhaW1wb3J0YW50OyB9CmhlYWRlcltkYXRhLXRlc3RpZD0ic3RIZWFkZXIiXSB7IGRpc3BsYXk6IG5vbmUgIWltcG9ydGFudDsgfQpmb290ZXIgeyBkaXNwbGF5OiBub25lICFpbXBvcnRhbnQ7IH0KW2RhdGEtdGVzdGlkPSJzdFRvb2xiYXIiXSB7IGRpc3BsYXk6IG5vbmUgIWltcG9ydGFudDsgfQpbZGF0YS10ZXN0aWQ9InN0RGVjb3JhdGlvbiJdIHsgZGlzcGxheTogbm9uZSAhaW1wb3J0YW50OyB9CltkYXRhLXRlc3RpZD0ic3RTaWRlYmFyIl0geyBkaXNwbGF5OiBmbGV4ICFpbXBvcnRhbnQ7IHZpc2liaWxpdHk6IHZpc2libGUgIWltcG9ydGFudDsgb3BhY2l0eTogMSAhaW1wb3J0YW50OyB3aWR0aDogMjYwcHggIWltcG9ydGFudDsgbWluLXdpZHRoOiAyNjBweCAhaW1wb3J0YW50OyB0cmFuc2Zvcm06IG5vbmUgIWltcG9ydGFudDsgcG9zaXRpb246IHJlbGF0aXZlICFpbXBvcnRhbnQ7IH0Kc2VjdGlvbltkYXRhLXRlc3RpZD0ic3RTaWRlYmFyIl0geyBkaXNwbGF5OiBmbGV4ICFpbXBvcnRhbnQ7IH0KLmJsb2NrLWNvbnRhaW5lciB7IHBhZGRpbmc6IDJyZW0gMnJlbSAycmVtICFpbXBvcnRhbnQ7IG1heC13aWR0aDogMTIwMHB4ICFpbXBvcnRhbnQ7IH0KPC9zdHlsZT4KIiIiLCB1bnNhZmVfYWxsb3dfaHRtbD1UcnVlKQoKIyDilIDilIAgQ09OU1RBTlRFUyDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAKVVNVQVJJT1MgPSB7CiAgICAidGFtaXJlcyI6IHsic2VuaGEiOiAiOWNkMnIxMVF2T3FEOGEiLCAiZXF1aXBlIjogInRhbWlyZXMiLCAicm9sZSI6ICJhZG1pbiIsICAibm9tZSI6ICJUYW1pcmVzIn0sCiAgICAibHVjaWFubyI6IHsic2VuaGEiOiAiVENMZW1EaldTR3YheXoiLCAiZXF1aXBlIjogImx1Y2lhbm8iLCAicm9sZSI6ICJnZXN0b3IiLCAibm9tZSI6ICJMdWNpYW5vIn0sCiAgICAiZGVib3JhaCI6IHsic2VuaGEiOiAiTDRmMTBJSm81YkdKM08iLCAiZXF1aXBlIjogImRlYm9yYWgiLCAicm9sZSI6ICJnZXN0b3IiLCAibm9tZSI6ICJEw6lib3JhaCJ9LAogICAgInZlbG9zbyI6ICB7InNlbmhhIjogIlUyQiFuaUpIN1c5NnJMIiwgImVxdWlwZSI6IE5vbmUsICAgICAgInJvbGUiOiAiZGlyZXRvciIsIm5vbWUiOiAiVmVsb3NvIn0sCiAgICAibW95YXJhIjogIHsic2VuaGEiOiAidWc4b21lUDRDdnQzbmwiLCAiZXF1aXBlIjogTm9uZSwgICAgICAicm9sZSI6ICJkaXJldG9yIiwibm9tZSI6ICJNb3lhcmEifSwKICAgICJnYWJyaWVsIjogeyJzZW5oYSI6ICJnYWJyaWVsMTIzIiwgICAgICAiZXF1aXBlIjogIm1ldGNvb2wiLCAicm9sZSI6ICJnZXN0b3IiLCAibm9tZSI6ICJHYWJyaWVsIn0sCn0KCkVRVUlQRVMgPSB7CiAgICAiZGFuaWxvIjogIHsibm9tZSI6ICJEYW5pbG8iLCAgImNvciI6ICIjMmRhZjVjIn0sCiAgICAiZGVib3JhaCI6IHsibm9tZSI6ICJEw6lib3JhaCIsICJjb3IiOiAiI2E4NTVmNyJ9LAogICAgInRhbWlyZXMiOiB7Im5vbWUiOiAiVGFtaXJlcyIsICJjb3IiOiAiI2Y5NzMxNiJ9LAp9CgojIE1hcGVhbWVudG8gbm9tZSDihpIgZXF1aXBlICgyIHByaW1laXJvcyBub21lcyBwYXJhIG1hdGNoKQpPUEVSQURPUkVTX0VRVUlQRSA9IHsKICAgICMgRXF1aXBlIERhbmlsbyDigJQgbm9tZXMgZXhhdG9zIGRvIGJhbmNvCiAgICAiaGV2ZXJ0b24gdGF2YXJlcyI6ICAgICAgImRhbmlsbyIsCiAgICAiaGV2ZXJ0b24gZmVsaWNpYW5vIjogICAgImRhbmlsbyIsCiAgICAiaGV2ZXJ0b24gZG9zIjogICAgICAgICAgImRhbmlsbyIsCiAgICAiZWR1YXJkYSBzYW5xdWV0YSI6ICAgICAgImRhbmlsbyIsCiAgICAiZWR1YXJkYSBjYXJ2YWxobyI6ICAgICAgImRhbmlsbyIsCiAgICAia2V0bGUgc2lsdmEiOiAgICAgICAgICAgImRhbmlsbyIsCiAgICAia2V0bGUgbG95YW5lIjogICAgICAgICAgImRhbmlsbyIsCiAgICAia2V0bGUgZGlhcyI6ICAgICAgICAgICAgImRhbmlsbyIsCiAgICAibWFyaWEgY2xhcmEiOiAgICAgICAgICAgImRhbmlsbyIsCiAgICAibGF1cmEgc2lsdmEiOiAgICAgICAgICAgImRhbmlsbyIsCiAgICAibGF1cmEgYmVhdHJpeiI6ICAgICAgICAgImRhbmlsbyIsCiAgICAiYW1hbmRhIGNsYXJhIjogICAgICAgICAgImRhbmlsbyIsCiAgICAjIEVxdWlwZSBEw6lib3JhaAogICAgImFtYW5kYSBlZHVhcmRhIjogICAgICAgICJkZWJvcmFoIiwKICAgICJuaWNvbGUga2FtaWxseSI6ICAgICAgICAiZGVib3JhaCIsCiAgICAibmljb2xlIGFtYXJhbCI6ICAgICAgICAgImRlYm9yYWgiLAogICAgInNhcmEgcGVyZWlyYSI6ICAgICAgICAgICJkZWJvcmFoIiwKICAgICJzaWx5ZSBmZXJyZWlyYSI6ICAgICAgICAiZGVib3JhaCIsCiAgICAic3lsaWUgZmVycmVpcmEiOiAgICAgICAgImRlYm9yYWgiLAogICAgImRpZWdvIHNvYXJlcyI6ICAgICAgICAgICJkZWJvcmFoIiwKICAgICJpdGFsbyBoZW5yaXF1ZSI6ICAgICAgICAiZGVib3JhaCIsCiAgICAiYnJlbm8gbWVuZG9uw6dhIjogICAgICAgICJkZWJvcmFoIiwKICAgICJicmVubyBtZW5kb25jYSI6ICAgICAgICAiZGVib3JhaCIsCiAgICAjIEVxdWlwZSBUYW1pcmVzCiAgICAid3luYXJhIGRvcyI6ICAgICAgICAgICAgInRhbWlyZXMiLAogICAgInd5bmFyYSByZWlzIjogICAgICAgICAgICJ0YW1pcmVzIiwKICAgICJhbmRyZSBnb21lcyI6ICAgICAgICAgICAidGFtaXJlcyIsCiAgICAiYW5kcsOpIGdvbWVzIjogICAgICAgICAgICJ0YW1pcmVzIiwKICAgICJ3YW5lc3NhIGRhIjogICAgICAgICAgICAidGFtaXJlcyIsCiAgICAid2FuZXNzYSBjYXJkb3NvIjogICAgICAgInRhbWlyZXMiLAogICAgImxvcmVuYSBjcmlzdGluYSI6ICAgICAgICJ0YW1pcmVzIiwKICAgICJsb3JlbmEgZ2FyY2lhIjogICAgICAgICAidGFtaXJlcyIsCiAgICAiY2FtaWxhIG5hcmEiOiAgICAgICAgICAgInRhbWlyZXMiLAogICAgImpoZW5pZmZlciBoZWxsZW4iOiAgICAgICJ0YW1pcmVzIiwKICAgICJqaGVuaWZmZXIgc2FudG9zIjogICAgICAidGFtaXJlcyIsCiAgICAibWFyY2VsbGUgc2FtcGFpbyI6ICAgICAgInRhbWlyZXMiLAogICAgImdyYXNpZWxsZSBkYSI6ICAgICAgICAgICJ0YW1pcmVzIiwKICAgICJncmFzaWVsbGUgc2FudG9zIjogICAgICAidGFtaXJlcyIsCn0KCk1FU0VTX05PTUVTID0gWyJKYW5laXJvIiwiRmV2ZXJlaXJvIiwiTWFyw6dvIiwiQWJyaWwiLCJNYWlvIiwiSnVuaG8iLAogICAgICAgICAgICAgICAiSnVsaG8iLCJBZ29zdG8iLCJTZXRlbWJybyIsIk91dHVicm8iLCJOb3ZlbWJybyIsIkRlemVtYnJvIl0KClNFTUFOQVNfTU9OSVRPUklBID0gWwogICAgIjHCqiBTZW1hbmEg4oCUIDHCqiBNb25pdG9yaWEiLCAiMcKqIFNlbWFuYSDigJQgMsKqIE1vbml0b3JpYSIsCiAgICAiMsKqIFNlbWFuYSDigJQgMcKqIE1vbml0b3JpYSIsICIywqogU2VtYW5hIOKAlCAywqogTW9uaXRvcmlhIiwKICAgICIzwqogU2VtYW5hIOKAlCAxwqogTW9uaXRvcmlhIiwgIjPCqiBTZW1hbmEg4oCUIDLCqiBNb25pdG9yaWEiLAogICAgIjTCqiBTZW1hbmEg4oCUIDHCqiBNb25pdG9yaWEiLCAiNMKqIFNlbWFuYSDigJQgMsKqIE1vbml0b3JpYSIsCl0KCiMg4pSA4pSAIE5PVk9TIENSSVTDiVJJT1MgKEZpY2hhIGlHcmVlbiAyMDI2KSDilIDilIDilIDilIDilIDilIDilIDilIAKQ1JJVEVSSU9TX1BBRFJBTyA9IFsKICAgIHsKICAgICAgICAiaWQiOiAiYzEiLCAibnVtIjogIjHCuiIsICJub21lIjogIkFiZXJ0dXJhIGUgSWRlbnRpZmljYcOnw6NvIiwgInBlc28iOiA1LCAib2JyaWdhdG9yaW8iOiBGYWxzZSwKICAgICAgICAiaXRlbnMiOiBbCiAgICAgICAgICAgICJSZWFsaXphIGEgcHJpbWVpcmEgaW50ZXJhw6fDo28gZW0gYXTDqSA1IHNlZ3VuZG9zIGFww7NzIG8gaW7DrWNpbyBkYSBsaWdhw6fDo28iLAogICAgICAgICAgICAiQ2hhbWEgbyBjbGllbnRlIHBlbG8gbm9tZSIsCiAgICAgICAgICAgICJBcHJlc2VudGEtc2UgcGVsbyBwcsOzcHJpbyBub21lIiwKICAgICAgICAgICAgIklkZW50aWZpY2EgYSBlbXByZXNhIGNvbW8gaUdyZWVuIgogICAgICAgIF0KICAgIH0sCiAgICB7CiAgICAgICAgImlkIjogImMyIiwgIm51bSI6ICIywroiLCAibm9tZSI6ICJDb211bmljYcOnw6NvIGUgUG9zdHVyYSIsICJwZXNvIjogMzAsICJvYnJpZ2F0b3JpbyI6IEZhbHNlLAogICAgICAgICJpdGVucyI6IFsKICAgICAgICAgICAgIlV0aWxpemEgdG9tIGNvcmRpYWwgZSBlbXDDoXRpY28iLAogICAgICAgICAgICAiRGVtb25zdHJhIGludGVyZXNzZSwgZW5nYWphbWVudG8gZSBzZW5zbyBkZSB1cmfDqm5jaWEgbmEgdHJhdGF0aXZhIiwKICAgICAgICAgICAgIkFwcmVzZW50YSAnc29ycmlzbyBuYSB2b3onLCBlc2N1dGEgYXRpdmEgZSBwb3N0dXJhIGNvbGFib3JhdGl2YS9wb3NpdGl2YSIsCiAgICAgICAgICAgICJVdGlsaXphIGNvbXVuaWNhw6fDo28gY2xhcmEgZSBhZGVxdWFkYSIsCiAgICAgICAgICAgICJFdml0YSBlcnJvcyBkZSBwcm9uw7puY2lhIGUgdsOtY2lvcyBkZSBsaW5ndWFnZW0gKGfDrXJpYXMsIGdlcnVuZGlzbW8sIGFicmV2aWHDp8O1ZXMgaW5hZGVxdWFkYXMpIgogICAgICAgIF0KICAgIH0sCiAgICB7CiAgICAgICAgImlkIjogImMzIiwgIm51bSI6ICIzwroiLCAibm9tZSI6ICJEaWFnbsOzc3RpY28gZGEgRMOtdmlkYSIsICJwZXNvIjogMjUsICJvYnJpZ2F0b3JpbyI6IEZhbHNlLAogICAgICAgICJpdGVucyI6IFsKICAgICAgICAgICAgIlJlYWxpemEgcGVyZ3VudGFzIGNsYXJhcywgb2JqZXRpdmFzIGUgcmVsZXZhbnRlcyBwYXJhIGNvbXByZWVuZGVyIGEgc2l0dWHDp8OjbyIsCiAgICAgICAgICAgICJJZGVudGlmaWNhIGNvcnJldGFtZW50ZSBvIG1vdGl2byBkYSBpbmFkaW1wbMOqbmNpYSIsCiAgICAgICAgICAgICJWZXJpZmljYSBzZSBvIGNsaWVudGUgc2UgcmVjb3JkYSBkbyBjb250cmF0byIsCiAgICAgICAgICAgICJDb25maXJtYSBzZSBvIGNsaWVudGUgcmVjZWJldSBvIGJvbGV0byIsCiAgICAgICAgICAgICJJbnZlc3RpZ2EgYSBwcmV2aXPDo28gZGUgcGFnYW1lbnRvIGUgZGVtYWlzIGluZm9ybWHDp8O1ZXMgbmVjZXNzw6FyaWFzIgogICAgICAgIF0KICAgIH0sCiAgICB7CiAgICAgICAgImlkIjogImM0IiwgIm51bSI6ICI0wroiLCAibm9tZSI6ICJSZWdpc3Ryb3MgZSBQcm9jZWRpbWVudG9zIiwgInBlc28iOiA1LCAib2JyaWdhdG9yaW8iOiBGYWxzZSwKICAgICAgICAiaXRlbnMiOiBbCiAgICAgICAgICAgICJSZWFsaXphIG8gcmVnaXN0cm8gY29ycmV0byBubyBzaXN0ZW1hIiwKICAgICAgICAgICAgIkNsYXNzaWZpY2EgYWRlcXVhZGFtZW50ZSBhIGxpZ2HDp8OjbyIKICAgICAgICBdCiAgICB9LAogICAgewogICAgICAgICJpZCI6ICJjNSIsICJudW0iOiAiNcK6IiwgIm5vbWUiOiAiQ29uZm9ybWlkYWRlIC8gQ29uZHXDp8OjbyBkYSBSZXRlbsOnw6NvIiwgInBlc28iOiAxMCwgIm9icmlnYXRvcmlvIjogRmFsc2UsCiAgICAgICAgIml0ZW5zIjogWwogICAgICAgICAgICAiSWRlbnRpZmljYSBhIGNhdXNhIGRvIGNhbmNlbGFtZW50byBlIGNvbmR1eiBhIHRyYXRhdGl2YSBkZSBmb3JtYSBhc3NlcnRpdmEiLAogICAgICAgICAgICAiVXRpbGl6YSBhcmd1bWVudG9zIHBlcnNvbmFsaXphZG9zIHBhcmEgc3VwZXJhciBvYmplw6fDtWVzIiwKICAgICAgICAgICAgIkRlbW9uc3RyYSBjcmlhdGl2aWRhZGUsIHBlcmNlcMOnw6NvIGUgcGVyc3Vhc8OjbyIsCiAgICAgICAgICAgICJBdHVhIG5hIGNhdXNhLXJhaXogZGEgb2JqZcOnw6NvIGUgY29uZHV6IGEgcmV0ZW7Dp8OjbyBkZSBhY29yZG8gY29tIGEgc2l0dWHDp8OjbyBkbyBjbGllbnRlIgogICAgICAgIF0KICAgIH0sCiAgICB7CiAgICAgICAgImlkIjogImM2IiwgIm51bSI6ICI2wroiLCAibm9tZSI6ICJpR3JlZW4gQ2x1YiDigJQgYXByZXNlbnRhw6fDo28gZSBiZW5lZsOtY2lvcyIsICJwZXNvIjogMjAsICJvYnJpZ2F0b3JpbyI6IFRydWUsCiAgICAgICAgIml0ZW5zIjogWwogICAgICAgICAgICAiISBPYnJpZ2F0w7NyaW86IFZlcmlmaWNhIHNlIG8gY2xpZW50ZSBqw6EgcG9zc3VpIG8gYXBsaWNhdGl2byBpR3JlZW4gQ2x1YiIsCiAgICAgICAgICAgICIhIE9icmlnYXTDs3JpbzogQXByZXNlbnRhIHZlcmJhbG1lbnRlIHBlbG8gbWVub3MgMiB2YW50YWdlbnMvYmVuZWbDrWNpb3MgZG8gaUdyZWVuIENsdWIgZHVyYW50ZSBhIGxpZ2HDp8OjbyIKICAgICAgICBdCiAgICB9LAogICAgewogICAgICAgICJpZCI6ICJjNyIsICJudW0iOiAiN8K6IiwgIm5vbWUiOiAiRW5jZXJyYW1lbnRvIiwgInBlc28iOiA1LCAib2JyaWdhdG9yaW8iOiBGYWxzZSwKICAgICAgICAiaXRlbnMiOiBbCiAgICAgICAgICAgICJSZWFsaXphIG8gZW5jZXJyYW1lbnRvIGRlIGZvcm1hIGFkZXF1YWRhIGUgY29yZGlhbCIsCiAgICAgICAgICAgICJQZXJndW50YSBzZSBvIGNsaWVudGUgcG9zc3VpIGFsZ3VtYSBkw7p2aWRhIG91IG5lY2Vzc2lkYWRlIGFkaWNpb25hbCIsCiAgICAgICAgICAgICJRdWFuZG8gaG91dmVyIG5lZ29jaWHDp8OjbywgcmVmb3LDp2EgYXMgY29uZGnDp8O1ZXMgZGEgbmVnb2NpYcOnw6NvIHJlYWxpemFkYSIKICAgICAgICBdCiAgICB9LApdCgpFUlJPU19DUklUSUNPU19QQURSQU8gPSBbCiAgICB7ImlkIjogImUxIiwgIm5vbWUiOiAiUG9zdHVyYSByw61zcGlkYSwgZGVzcmVzcGVpdG9zYSBvdSBhbnRpw6l0aWNhIiwKICAgICAiZGVzYyI6ICJSdWRlemEsIGltcGFjacOqbmNpYSwgaXJyaXRhw6fDo28sIHByZXNzw6NvIGluZGV2aWRhLCBkZXNyZXNwZWl0bywgaXJvbmlhLCBkZWJvY2hlLCBsaW5ndWFnZW0gZGUgYmFpeG8gY2Fsw6NvLCBjb252ZXJzYXMgcGFyYWxlbGFzIGVtIGNhbmFsIGFiZXJ0bywgZGlmYW1hw6fDo28vY2Fsw7puaWEgY29udHJhIGEgaUdyZWVuIG91IHBhcmNlaXJvcyJ9LAogICAgeyJpZCI6ICJlMiIsICJub21lIjogIkZhbGhhIGdyYXZlIG5hIGFiZXJ0dXJhIG91IGVuY2VycmFtZW50byIsCiAgICAgImRlc2MiOiAiTsOjbyByZWFsaXphciBhIHByaW1laXJhIGludGVyYcOnw6NvIGVtIGF0w6kgMTAgc2VndW5kb3Mgb3UgZWZldHVhciBkZXNjb25leMOjby9lbmNlcnJhbWVudG8gaW5hZGVxdWFkbyBzZW0gY29uY2x1c8OjbyBkYSB0cmF0YXRpdmEifSwKICAgIHsiaWQiOiAiZTMiLCAibm9tZSI6ICJBYmFuZG9ubyBkbyBjbGllbnRlIiwKICAgICAiZGVzYyI6ICJOw6NvIHJlc3BvbmRlciBxdWFuZG8gbyBjbGllbnRlIHJldG9ybmFyIGR1cmFudGUgdW1hIHBhdXNhIG91IGNvbnN1bHRhIn0sCiAgICB7ImlkIjogImU0IiwgIm5vbWUiOiAiSW5mb3JtYcOnw6NvIGluY29ycmV0YSwgaW5jb21wbGV0YSBvdSBpbnZlcsOtZGljYSIsCiAgICAgImRlc2MiOiAiQ29tIHBvdGVuY2lhbCBkZSBjYXVzYXIgcHJlanXDrXpvIGZpbmFuY2Vpcm8gb3UgZGUgaW1hZ2VtLCBpbmNsdWluZG8gcHJvbWV0ZXIgYm9sZXRvLCBsaWdhw6fDo28sIHByaW9yaXphw6fDo28gb3UgcXVhbHF1ZXIgYcOnw6NvIG7Do28gcmVhbGl6YWRhLCBiZW0gY29tbyBlbnZpbyBpbmNvcnJldG8gZGUgYm9sZXRvIn0sCiAgICB7ImlkIjogImU1IiwgIm5vbWUiOiAiRmFsaGEgZ3JhdmUgbmEgYXJndW1lbnRhw6fDo28gZGUgcmV0ZW7Dp8OjbyIsCiAgICAgImRlc2MiOiAiTsOjbyByZWFsaXphciB0ZW50YXRpdmEgZWZldGl2YSBkZSByZXRlbsOnw6NvIGRpYW50ZSBkZSBpbnRlbsOnw6NvIGNsYXJhIGRlIGNhbmNlbGFtZW50bywgbsOjbyBidXNjYXIgc3VwZXJhciBhIG9iamXDp8OjbyBvdSBuw6NvIGFwcmVzZW50YXIgYWx0ZXJuYXRpdmEgcXVlIHBvZGVyaWEgZXZpdGFyIG8gY2FuY2VsYW1lbnRvIn0sCiAgICB7ImlkIjogImU2IiwgIm5vbWUiOiAiUmV0ZW7Dp8OjbyBpbmRldmlkYSBkYSBsaWdhw6fDo28iLAogICAgICJkZXNjIjogIk1hbnRlciBvIGNsaWVudGUgZW0gZXNwZXJhL2xpbmhhIHNlbSBuZWNlc3NpZGFkZSBvdSBqdXN0aWZpY2F0aXZhIn0sCl0KCkZBSVhBU19QT05UT1MgPSBbKDAsNzAsMCksKDcxLDgwLDMwMCksKDgxLDkwLDUwMCksKDkxLDk1LDcwMCksKDk2LDk5LDEwMDApLCgxMDAsMTAwLDExMDApXQoKIyDilIDilIAgTU9OR09EQiDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAKQHN0LmNhY2hlX3Jlc291cmNlCmRlZiBnZXRfZGIoKToKICAgIGNsaWVudCA9IE1vbmdvQ2xpZW50KAogICAgICAgIHN0LnNlY3JldHNbIm1vbmdvIl1bInVyaSJdLAogICAgICAgIHNlcnZlclNlbGVjdGlvblRpbWVvdXRNUz01MDAwLAogICAgICAgIGNvbm5lY3RUaW1lb3V0TVM9NTAwMCwKICAgICAgICBzb2NrZXRUaW1lb3V0TVM9MTUwMDAsCiAgICAgICAgbWF4UG9vbFNpemU9MTAsCiAgICAgICAgcmV0cnlXcml0ZXM9VHJ1ZSwKICAgICkKICAgIHJldHVybiBjbGllbnRbc3Quc2VjcmV0c1sibW9uZ28iXVsiZGIiXV0KCmRlZiBnZXRfY3JpdGVyaW9zKCk6CiAgICB0cnk6CiAgICAgICAgZG9jID0gZ2V0X2RiKCkuY29uZmlndXJhY29lcy5maW5kX29uZSh7Il9pZCI6ICJjcml0ZXJpb3NfbW9uaXRvcmlhIn0pCiAgICAgICAgaWYgZG9jIGFuZCBkb2MuZ2V0KCJjcml0ZXJpb3MiKToKICAgICAgICAgICAgcmV0dXJuIGRvY1siY3JpdGVyaW9zIl0KICAgIGV4Y2VwdDoKICAgICAgICBwYXNzCiAgICByZXR1cm4gQ1JJVEVSSU9TX1BBRFJBTwoKZGVmIHNhbHZhcl9jcml0ZXJpb3MoYyk6CiAgICBnZXRfZGIoKS5jb25maWd1cmFjb2VzLnVwZGF0ZV9vbmUoCiAgICAgICAgeyJfaWQiOiAiY3JpdGVyaW9zX21vbml0b3JpYSJ9LAogICAgICAgIHsiJHNldCI6IHsiX2lkIjogImNyaXRlcmlvc19tb25pdG9yaWEiLCAiY3JpdGVyaW9zIjogYywgImF0dWFsaXphZG9FbSI6IGRhdGV0aW1lLm5vdygpfX0sCiAgICAgICAgdXBzZXJ0PVRydWUKICAgICkKCmRlZiBnZXRfZXJyb3NfY3JpdGljb3MoKToKICAgIHRyeToKICAgICAgICBkb2MgPSBnZXRfZGIoKS5jb25maWd1cmFjb2VzLmZpbmRfb25lKHsiX2lkIjogImVycm9zX2NyaXRpY29zX21vbml0b3JpYSJ9KQogICAgICAgIGlmIGRvYyBhbmQgZG9jLmdldCgiZXJyb3MiKToKICAgICAgICAgICAgcmV0dXJuIGRvY1siZXJyb3MiXQogICAgZXhjZXB0OgogICAgICAgIHBhc3MKICAgIHJldHVybiBFUlJPU19DUklUSUNPU19QQURSQU8KCmRlZiBzYWx2YXJfZXJyb3NfY3JpdGljb3MoZSk6CiAgICBnZXRfZGIoKS5jb25maWd1cmFjb2VzLnVwZGF0ZV9vbmUoCiAgICAgICAgeyJfaWQiOiAiZXJyb3NfY3JpdGljb3NfbW9uaXRvcmlhIn0sCiAgICAgICAgeyIkc2V0IjogeyJfaWQiOiAiZXJyb3NfY3JpdGljb3NfbW9uaXRvcmlhIiwgImVycm9zIjogZSwgImF0dWFsaXphZG9FbSI6IGRhdGV0aW1lLm5vdygpfX0sCiAgICAgICAgdXBzZXJ0PVRydWUKICAgICkKCkBzdC5jYWNoZV9kYXRhKHR0bD0zNjAwKQpkZWYgYnVzY2FyX29wZXJhZG9yZXMoZXEpOgogICAgb3BzID0gbGlzdChnZXRfZGIoKS5vcGVyYWRvcmVzLmZpbmQoeyJlcXVpcGVJZCI6IGVxfSkuc29ydCgibm9tZSIsIDEpKQogICAgdmlzdG9zID0gc2V0KCkKICAgIHVuaWNvcyA9IFtdCiAgICBmb3Igb3AgaW4gb3BzOgogICAgICAgIG5vbWVfbm9ybSA9IG9wLmdldCgibm9tZSIsICIiKS5zdHJpcCgpLmxvd2VyKCkKICAgICAgICBpZiBub21lX25vcm0gbm90IGluIHZpc3RvczoKICAgICAgICAgICAgdmlzdG9zLmFkZChub21lX25vcm0pCiAgICAgICAgICAgIHVuaWNvcy5hcHBlbmQob3ApCiAgICByZXR1cm4gdW5pY29zCgpkZWYgbWlncmFyX29wZXJhZG9yZXMoKTo="
PREMIACAO_HTML = _b64.b64decode(_HTML_B64).decode("utf-8")


st.set_page_config(
    page_title="iGreen Monitorias",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #f0f7f0 !important; }
[data-testid="stSidebar"] { background: #f5fbf5 !important; border-right: 1px solid #d0e8d0 !important; }
[data-testid="stSidebar"] .stRadio > div > p { display: none !important; }
[data-testid="stSidebar"] .stRadio label {
    color: #2d4a2d !important; font-size: 13px !important; font-weight: 500 !important;
    padding: 10px 16px !important; display: flex !important; align-items: center !important;
    border-radius: 8px !important; margin: 1px 0 !important; width: 100% !important;
    background: #ffffff !important; border: 1px solid #d8ead8 !important;
    min-height: 40px !important; transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #edf7ed !important; border-color: #2e7d32 !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    color: #ffffff !important; background: #2e7d32 !important; border-color: #2e7d32 !important; font-weight: 600 !important;
}
[data-testid="stMetric"] { background: #ffffff !important; border: 1px solid #e0e8e0 !important; border-radius: 10px !important; padding: 16px 20px !important; border-top: 3px solid #2e7d32 !important; }
[data-testid="stMetricValue"] { color: #1a2e1a !important; font-size: 16px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #5a8a5a !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.stButton > button { background: #f0f7f0 !important; color: #2e7d32 !important; border: 1px solid #c8e0c8 !important; border-radius: 6px !important; font-weight: 500 !important; font-size: 12px !important; }
.stButton > button:hover { background: #2e7d32 !important; color: #ffffff !important; }
h1 { color: #1a2e1a !important; font-size: 20px !important; font-weight: 700 !important; }
h2 { color: #2d4a2d !important; font-size: 16px !important; font-weight: 600 !important; }
p { color: #1a3a1a !important; font-size: 13px; }
hr { border: none !important; border-top: 1px solid #e0e8e0 !important; margin: 14px 0 !important; }
.stTextInput input, .stNumberInput input, .stTextArea textarea { background: #ffffff !important; border: 1px solid #c8e0c8 !important; color: #1a2e1a !important; border-radius: 8px !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #ffffff !important; border: 1px solid #c8e0c8 !important; color: #1a2e1a !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab-list"] { background: #f0f7f0 !important; border-radius: 8px !important; padding: 4px !important; border: 1px solid #c8e0c8 !important; }
.stTabs [data-baseweb="tab"] { color: #5a8a5a !important; border-radius: 6px !important; font-size: 12px !important; }
.stTabs [aria-selected="true"] { background: #2e7d32 !important; color: #ffffff !important; }
.stSuccess > div { background: #f0faf0 !important; border-left: 3px solid #2e7d32 !important; color: #2e7d32 !important; border-radius: 8px !important; }
.stError > div { background: #fff5f5 !important; border-left: 3px solid #c62828 !important; color: #c62828 !important; border-radius: 8px !important; }
.stWarning > div { background: #fffbf0 !important; border-left: 3px solid #f0c000 !important; color: #8a6a00 !important; border-radius: 8px !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
button[data-testid="baseButton-header"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"] { display: flex !important; visibility: visible !important; opacity: 1 !important; width: 260px !important; min-width: 260px !important; transform: none !important; position: relative !important; }
section[data-testid="stSidebar"] { display: flex !important; }
.block-container { padding: 2rem 2rem 2rem !important; max-width: 1200px !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ──────────────────────────────────
USUARIOS = {
    "tamires": {"senha": "9cd2r11QvOqD8a", "equipe": "tamires", "role": "admin",  "nome": "Tamires"},
    "luciano": {"senha": "TCLemDjWSGv!yz", "equipe": "luciano", "role": "gestor", "nome": "Luciano"},
    "deborah": {"senha": "L4f10IJo5bGJ3O", "equipe": "deborah", "role": "gestor", "nome": "Déborah"},
    "veloso":  {"senha": "U2B!niJH7W96rL", "equipe": None,      "role": "diretor","nome": "Veloso"},
    "moyara":  {"senha": "ug8omeP4Cvt3nl", "equipe": None,      "role": "diretor","nome": "Moyara"},
    "gabriel": {"senha": "gabriel123",      "equipe": "metcool", "role": "gestor", "nome": "Gabriel"},
}

EQUIPES = {
    "danilo":  {"nome": "Danilo",  "cor": "#2daf5c"},
    "deborah": {"nome": "Déborah", "cor": "#a855f7"},
    "tamires": {"nome": "Tamires", "cor": "#f97316"},
}

# Mapeamento nome → equipe (2 primeiros nomes para match)
OPERADORES_EQUIPE = {
    # Equipe Danilo — nomes exatos do banco
    "heverton tavares":      "danilo",
    "heverton feliciano":    "danilo",
    "heverton dos":          "danilo",
    "eduarda sanqueta":      "danilo",
    "eduarda carvalho":      "danilo",
    "ketle silva":           "danilo",
    "ketle loyane":          "danilo",
    "ketle dias":            "danilo",
    "maria clara":           "danilo",
    "laura silva":           "danilo",
    "laura beatriz":         "danilo",
    "amanda clara":          "danilo",
    # Equipe Déborah
    "amanda eduarda":        "deborah",
    "nicole kamilly":        "deborah",
    "nicole amaral":         "deborah",
    "sara pereira":          "deborah",
    "silye ferreira":        "deborah",
    "sylie ferreira":        "deborah",
    "diego soares":          "deborah",
    "italo henrique":        "deborah",
    "breno mendonça":        "deborah",
    "breno mendonca":        "deborah",
    # Equipe Tamires
    "wynara dos":            "tamires",
    "wynara reis":           "tamires",
    "andre gomes":           "tamires",
    "andré gomes":           "tamires",
    "wanessa da":            "tamires",
    "wanessa cardoso":       "tamires",
    "lorena cristina":       "tamires",
    "lorena garcia":         "tamires",
    "camila nara":           "tamires",
    "jheniffer hellen":      "tamires",
    "jheniffer santos":      "tamires",
    "marcelle sampaio":      "tamires",
    "grasielle da":          "tamires",
    "grasielle santos":      "tamires",
}

MESES_NOMES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

SEMANAS_MONITORIA = [
    "1ª Semana — 1ª Monitoria", "1ª Semana — 2ª Monitoria",
    "2ª Semana — 1ª Monitoria", "2ª Semana — 2ª Monitoria",
    "3ª Semana — 1ª Monitoria", "3ª Semana — 2ª Monitoria",
    "4ª Semana — 1ª Monitoria", "4ª Semana — 2ª Monitoria",
]

# ── NOVOS CRITÉRIOS (Ficha iGreen 2026) ────────
CRITERIOS_PADRAO = [
    {
        "id": "c1", "num": "1º", "nome": "Abertura e Identificação", "peso": 5, "obrigatorio": False,
        "itens": [
            "Realiza a primeira interação em até 5 segundos após o início da ligação",
            "Chama o cliente pelo nome",
            "Apresenta-se pelo próprio nome",
            "Identifica a empresa como iGreen"
        ]
    },
    {
        "id": "c2", "num": "2º", "nome": "Comunicação e Postura", "peso": 30, "obrigatorio": False,
        "itens": [
            "Utiliza tom cordial e empático",
            "Demonstra interesse, engajamento e senso de urgência na tratativa",
            "Apresenta 'sorriso na voz', escuta ativa e postura colaborativa/positiva",
            "Utiliza comunicação clara e adequada",
            "Evita erros de pronúncia e vícios de linguagem (gírias, gerundismo, abreviações inadequadas)"
        ]
    },
    {
        "id": "c3", "num": "3º", "nome": "Diagnóstico da Dívida", "peso": 25, "obrigatorio": False,
        "itens": [
            "Realiza perguntas claras, objetivas e relevantes para compreender a situação",
            "Identifica corretamente o motivo da inadimplência",
            "Verifica se o cliente se recorda do contrato",
            "Confirma se o cliente recebeu o boleto",
            "Investiga a previsão de pagamento e demais informações necessárias"
        ]
    },
    {
        "id": "c4", "num": "4º", "nome": "Registros e Procedimentos", "peso": 5, "obrigatorio": False,
        "itens": [
            "Realiza o registro correto no sistema",
            "Classifica adequadamente a ligação"
        ]
    },
    {
        "id": "c5", "num": "5º", "nome": "Conformidade / Condução da Retenção", "peso": 10, "obrigatorio": False,
        "itens": [
            "Identifica a causa do cancelamento e conduz a tratativa de forma assertiva",
            "Utiliza argumentos personalizados para superar objeções",
            "Demonstra criatividade, percepção e persuasão",
            "Atua na causa-raiz da objeção e conduz a retenção de acordo com a situação do cliente"
        ]
    },
    {
        "id": "c6", "num": "6º", "nome": "iGreen Club — apresentação e benefícios", "peso": 20, "obrigatorio": True,
        "itens": [
            "! Obrigatório: Verifica se o cliente já possui o aplicativo iGreen Club",
            "! Obrigatório: Apresenta verbalmente pelo menos 2 vantagens/benefícios do iGreen Club durante a ligação"
        ]
    },
    {
        "id": "c7", "num": "7º", "nome": "Encerramento", "peso": 5, "obrigatorio": False,
        "itens": [
            "Realiza o encerramento de forma adequada e cordial",
            "Pergunta se o cliente possui alguma dúvida ou necessidade adicional",
            "Quando houver negociação, reforça as condições da negociação realizada"
        ]
    },
]

ERROS_CRITICOS_PADRAO = [
    {"id": "e1", "nome": "Postura ríspida, desrespeitosa ou antiética",
     "desc": "Rudeza, impaciência, irritação, pressão indevida, desrespeito, ironia, deboche, linguagem de baixo calão, conversas paralelas em canal aberto, difamação/calúnia contra a iGreen ou parceiros"},
    {"id": "e2", "nome": "Falha grave na abertura ou encerramento",
     "desc": "Não realizar a primeira interação em até 10 segundos ou efetuar desconexão/encerramento inadequado sem conclusão da tratativa"},
    {"id": "e3", "nome": "Abandono do cliente",
     "desc": "Não responder quando o cliente retornar durante uma pausa ou consulta"},
    {"id": "e4", "nome": "Informação incorreta, incompleta ou inverídica",
     "desc": "Com potencial de causar prejuízo financeiro ou de imagem, incluindo prometer boleto, ligação, priorização ou qualquer ação não realizada, bem como envio incorreto de boleto"},
    {"id": "e5", "nome": "Falha grave na argumentação de retenção",
     "desc": "Não realizar tentativa efetiva de retenção diante de intenção clara de cancelamento, não buscar superar a objeção ou não apresentar alternativa que poderia evitar o cancelamento"},
    {"id": "e6", "nome": "Retenção indevida da ligação",
     "desc": "Manter o cliente em espera/linha sem necessidade ou justificativa"},
]

FAIXAS_PONTOS = [(0,70,0),(71,80,300),(81,90,500),(91,95,700),(96,99,1000),(100,100,1100)]

# ── MONGODB ─────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(
        st.secrets["mongo"]["uri"],
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=15000,
        maxPoolSize=10,
        retryWrites=True,
    )
    return client[st.secrets["mongo"]["db"]]

def get_criterios():
    try:
        doc = get_db().configuracoes.find_one({"_id": "criterios_monitoria"})
        if doc and doc.get("criterios"):
            return doc["criterios"]
    except:
        pass
    return CRITERIOS_PADRAO

def salvar_criterios(c):
    get_db().configuracoes.update_one(
        {"_id": "criterios_monitoria"},
        {"$set": {"_id": "criterios_monitoria", "criterios": c, "atualizadoEm": datetime.now()}},
        upsert=True
    )

def get_erros_criticos():
    try:
        doc = get_db().configuracoes.find_one({"_id": "erros_criticos_monitoria"})
        if doc and doc.get("erros"):
            return doc["erros"]
    except:
        pass
    return ERROS_CRITICOS_PADRAO

def salvar_erros_criticos(e):
    get_db().configuracoes.update_one(
        {"_id": "erros_criticos_monitoria"},
        {"$set": {"_id": "erros_criticos_monitoria", "erros": e, "atualizadoEm": datetime.now()}},
        upsert=True
    )

@st.cache_data(ttl=3600)
def buscar_operadores(eq):
    ops = list(get_db().operadores.find({"equipeId": eq}).sort("nome", 1))
    vistos = set()
    unicos = []
    for op in ops:
        nome_norm = op.get("nome", "").strip().lower()
        if nome_norm not in vistos:
            vistos.add(nome_norm)
            unicos.append(op)
    return unicos

def migrar_operadores():
    """Migra operadores para as novas equipes com base no nome. Roda uma vez."""
    import unicodedata
    def norm(s):
        s = unicodedata.normalize('NFKD', str(s).lower().strip()).encode('ascii','ignore').decode()
        return re.sub(r'\s+', ' ', s).strip()

    try:
        db = get_db()
        ops = list(db.operadores.find({}))
        migrados = 0
        for op in ops:
            nome_op = norm(op.get('nome', ''))
            palavras = nome_op.split()
            eq_nova = None
            # Tentar combinações: p1+p2, p1+p3, p1+p4, só p1
            combos = []
            if len(palavras) >= 2:
                combos.append(' '.join(palavras[:2]))
            if len(palavras) >= 3:
                combos.append(palavras[0] + ' ' + palavras[2])
            if len(palavras) >= 4:
                combos.append(palavras[0] + ' ' + palavras[3])
            combos.append(palavras[0] if palavras else nome_op)
            for combo in combos:
                eq_nova = OPERADORES_EQUIPE.get(combo)
                if eq_nova:
                    break
            if eq_nova and op.get('equipeId') != eq_nova:
                db.operadores.update_one(
                    {"_id": op["_id"]},
                    {"$set": {"equipeId": eq_nova}}
                )
                migrados += 1
        return migrados
    except Exception as e:
        return 0

def salvar_operador(eq, nome, pleno=False):
    oid = re.sub(r'[^a-z0-9]', '-', nome.lower().strip())
    oid = re.sub(r'-+', '-', oid).strip('-')
    oid = f"{eq[:3]}-{oid}"[:40]
    if not get_db().operadores.find_one({"_id": oid}):
        get_db().operadores.insert_one({"_id": oid, "equipeId": eq, "nome": nome, "pleno": pleno, "criadoEm": datetime.now()})
    return oid

def atualizar_operador(oid, nome, pleno):
    get_db().operadores.update_one({"_id": oid}, {"$set": {"nome": nome, "pleno": pleno}})

def excluir_operador(oid):
    get_db().operadores.delete_one({"_id": oid})

def salvar_monitoria(eq, oid, onome, prot, obs, crits, erros, nota, ma, semana=None):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    get_db().monitorias.insert_one({
        "_id": f"mon__{eq}__{oid}__{ts}",
        "equipeId": eq, "opId": oid, "opNome": onome,
        "protocolo": prot, "observacao": obs,
        "criterios": crits, "errosCriticos": erros,
        "nota": nota, "mesAno": ma, "semana_mon": semana,
        "criadoEm": datetime.now()
    })

def buscar_monitorias_operador(oid):
    op_doc = get_db().operadores.find_one({"_id": oid})
    ids_busca = [oid]
    if op_doc and op_doc.get('vinculadoA'):
        ids_busca.append(op_doc['vinculadoA'])
    return list(get_db().monitorias.find({"opId": {"$in": ids_busca}}).sort("criadoEm", -1))

def buscar_monitorias_equipe(eq, ma=None):
    # Busca todos os opIds da equipe atual
    ops = list(get_db().operadores.find({"equipeId": eq}))
    op_ids = [op["_id"] for op in ops]
    # Inclui também vinculadoA
    vinculados = [op.get("vinculadoA") for op in ops if op.get("vinculadoA")]
    op_ids += vinculados
    # Busca monitorias por opId OU por equipeId (para monitorias antigas)
    f = {"$or": [{"opId": {"$in": op_ids}}, {"equipeId": eq}]}
    if ma:
        f = {"$and": [{"$or": [{"opId": {"$in": op_ids}}, {"equipeId": eq}]}, {"mesAno": ma}]}
    return list(get_db().monitorias.find(f).sort("criadoEm", -1))

def excluir_monitoria(did):
    get_db().monitorias.delete_one({"_id": did})

@st.cache_data(ttl=3600)
def buscar_senha_usuario(uid):
    try:
        doc = get_db().usuarios_senhas.find_one({"_id": uid})
        if doc and doc.get("senha"):
            return doc["senha"]
    except:
        pass
    u = USUARIOS.get(uid)
    if u:
        return u.get("senha")
    return None

def salvar_senha_usuario(uid, nova_senha):
    get_db().usuarios_senhas.update_one(
        {"_id": uid},
        {"$set": {"_id": uid, "senha": nova_senha, "atualizadoEm": datetime.now()}},
        upsert=True
    )
    buscar_senha_usuario.clear()

# ── HELPERS ─────────────────────────────────────
def calc_pontos(media):
    import math
    m = math.floor(media + 0.5)
    for de, ate, pts in FAIXAS_PONTOS:
        if de <= m <= ate:
            return pts
    return 0

def calc_media_operador(oid, ma=None):
    monts = buscar_monitorias_operador(oid)
    if ma:
        monts = [m for m in monts if m.get("mesAno") == ma]
    if not monts:
        return 0, 0
    notas = [m["nota"] for m in monts if "nota" in m]
    if not notas:
        return 0, 0
    return round(sum(notas) / len(notas), 1), len(notas)

def get_status_media(media):
    if media == 0:   return "Zerada",      "#e53935", "#ffebee"
    if media >= 91:  return "Excelente",   "#2e7d32", "#e8f5e9"
    if media >= 81:  return "Bom",         "#1565c0", "#e3f2fd"
    if media >= 71:  return "Regular",     "#f57f17", "#fff8e1"
    return "Em desenvolvimento", "#6d4c41", "#efebe9"

def get_iniciais(nome):
    p = nome.strip().split()
    if len(p) >= 2:
        return (p[0][0] + p[1][0]).upper()
    return nome[:2].upper()

CORES_INICIAIS = ["#1565c0","#2e7d32","#6a1b9a","#bf360c","#00695c","#4527a0","#ad1457","#0277bd","#558b2f","#4e342e"]

def get_cor_inicial(nome):
    return CORES_INICIAIS[sum(ord(c) for c in nome) % len(CORES_INICIAIS)]

def get_todos_meses_ano(ano=None):
    if not ano:
        ano = datetime.now().year
    return [f"{m}-{ano}" for m in MESES_NOMES]

def get_anos_disponiveis():
    hoje = datetime.now()
    return [str(hoje.year), str(hoje.year - 1)]

def header_page(titulo, sub=""):
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;
                padding:22px 28px;margin-bottom:24px;border-left:4px solid #2e7d32;
                box-shadow:0 2px 8px rgba(0,0,0,0.06)">
        <h1 style="margin:0;color:#1a2e1a;font-size:20px;font-weight:700">{titulo}</h1>
        {"<p style='color:#5a8a5a;margin:4px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px'>"+sub+"</p>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def gerar_pdf_monitoria(onome, prot, obs, crits, erros, nota, media, n_mon, ma):
    pontos = calc_pontos(media)
    L = []
    L.append(f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a1a;margin:0;padding:0}}
.hdr{{background:#0a2414;color:#fff;padding:32px 40px}}
.logo{{font-size:24px;font-weight:800;color:#2daf5c}}
.body{{padding:32px 40px}}
.irow{{display:flex;gap:32px;margin-bottom:24px;background:#f8fdf9;border-radius:10px;padding:16px 20px;border-left:4px solid #2daf5c}}
.lbl{{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;font-weight:600}}
.val{{font-size:15px;font-weight:700;color:#0a2414;margin-top:2px}}
table{{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px}}
thead th{{background:#0a2414;color:#fff;padding:10px 14px;text-align:left}}
tbody tr:nth-child(even){{background:#f0f9f3}}
tbody td{{padding:10px 14px;border-bottom:1px solid #e0ede5}}
.ok{{color:#1a6b35;font-weight:700}}.no{{color:#c0392b;font-weight:700}}
.nbox{{background:#0a2414;color:#fff;border-radius:12px;padding:24px;text-align:center;margin-bottom:24px}}
.nnum{{font-size:48px;font-weight:800;color:#2daf5c}}
.mbox{{background:#f0f9f3;border:1px solid #c3e6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px;display:flex;gap:32px}}
.crit{{background:#fdf0f0;border:1px solid #f5c6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px}}
.obs{{background:#f8fdf9;border:1px solid #c3e6cb;border-radius:10px;padding:16px 20px;margin-bottom:24px}}
.foot{{background:#f0f9f3;padding:16px 40px;text-align:center;font-size:11px;color:#5a9a70;border-top:2px solid #2daf5c}}
</style></head><body>
<div class='hdr'><div class='logo'>iGREEN ENERGY</div>
<div style='font-size:13px;color:#5a9a70;margin-top:4px'>Relatório de Monitoria</div></div>
<div class='body'>
<div class='irow'>
  <div><div class='lbl'>Operador</div><div class='val'>{onome}</div></div>
  <div><div class='lbl'>Protocolo</div><div class='val'>{prot}</div></div>
  <div><div class='lbl'>Mês</div><div class='val'>{ma.replace('-',' ')}</div></div>
  <div><div class='lbl'>Data</div><div class='val'>{datetime.now().strftime('%d/%m/%Y')}</div></div>
</div>""")
    if erros:
        L.append("<div class='crit'><strong>MONITORIA ZERADA — Erro Crítico</strong><br>")
        for e in erros:
            L.append(f"• {e['nome']}<br>")
        L.append("</div>")
    L.append("<table><thead><tr><th>#</th><th>Critério</th><th>Peso</th><th>Resultado</th></tr></thead><tbody>")
    for c in crits:
        p = "<span class='ok'>Passou</span>" if c["passou"] else "<span class='no'>Não passou</span>"
        L.append(f"<tr><td>{c['num']}</td><td>{c['nome']}</td><td>{c['peso']}</td><td>{p}</td></tr>")
    L.append("</tbody></table>")
    L.append(f"<div class='nbox'><div style='font-size:13px;color:#5a9a70'>Nota desta Monitoria</div><div class='nnum'>{nota:.0f}%</div></div>")
    L.append(f"<div class='mbox'><div><div class='lbl'>Média ({n_mon} monitorias)</div><div style='font-size:24px;font-weight:800'>{media:.2f}%</div></div><div><div class='lbl'>Pontuação</div><div style='font-size:24px;font-weight:800;color:#1a6b35'>{pontos} pts</div></div></div>")
    if obs:
        L.append(f"<div class='obs'><strong>Observações:</strong><br>{obs}</div>")
    L.append(f"</div><div class='foot'>iGreen Energy · {datetime.now().strftime('%d/%m/%Y às %H:%M')}</div></body></html>")
    return "".join(L)

def gerar_relatorio_monitorias(eq, ma):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    ops = buscar_operadores(eq)
    monitorias = buscar_monitorias_equipe(eq, ma)

    for op in ops:
        vid = op.get('vinculadoA')
        if vid:
            mons_vinc = list(get_db().monitorias.find({"opId": vid, "mesAno": ma}))
            for m in mons_vinc:
                m['opId'] = op['_id']
                m['opNome'] = op['nome']
            monitorias.extend(mons_vinc)

    if not monitorias:
        return None

    semanas = SEMANAS_MONITORIA
    dados = {}
    for m in monitorias:
        oid = m.get('opId')
        nome = m.get('opNome', '')
        sem = m.get('semana_mon', '')
        nota = float(m.get('nota', 0))
        if oid not in dados:
            dados[oid] = {'nome': nome, 'semanas': {}}
        if sem not in dados[oid]['semanas']:
            dados[oid]['semanas'][sem] = []
        dados[oid]['semanas'][sem].append(nota)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Monitorias {ma}"

    cores_semanas = ["DCE9FF","DCE9FF","FFEFD5","FFEFD5","E8FFE8","E8FFE8","FFE4FF","FFE4FF"]
    verde = "1A3D2B"
    branco = "FFFFFF"
    cinza = "F2F4F3"

    ws.merge_cells("A1:A2")
    ws["A1"] = "Analista"
    ws["A1"].font = Font(bold=True, color=branco)
    ws["A1"].fill = PatternFill("solid", start_color=verde)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["A"].width = 30

    semana_grupos = [("1ª Semana", 2, 3), ("2ª Semana", 4, 5), ("3ª Semana", 6, 7), ("4ª Semana", 8, 9)]
    for label, col_ini, col_fim in semana_grupos:
        letra_ini = get_column_letter(col_ini)
        letra_fim = get_column_letter(col_fim)
        ws.merge_cells(f"{letra_ini}1:{letra_fim}1")
        ws[f"{letra_ini}1"] = label
        ws[f"{letra_ini}1"].font = Font(bold=True, color=verde)
        ws[f"{letra_ini}1"].alignment = Alignment(horizontal="center")
        ws[f"{letra_ini}1"].fill = PatternFill("solid", start_color=cores_semanas[col_ini-2])

    for i, col in enumerate(range(2, 10)):
        letra = get_column_letter(col)
        ws[f"{letra}2"] = "1ª Monitoria" if i % 2 == 0 else "2ª Monitoria"
        ws[f"{letra}2"].font = Font(bold=True)
        ws[f"{letra}2"].fill = PatternFill("solid", start_color=cores_semanas[i])
        ws[f"{letra}2"].alignment = Alignment(horizontal="center")
        ws.column_dimensions[letra].width = 12

    ws.merge_cells("J1:J2")
    ws["J1"] = "MÉDIA"
    ws["J1"].font = Font(bold=True, color=branco)
    ws["J1"].fill = PatternFill("solid", start_color=verde)
    ws["J1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["J"].width = 10

    row = 3
    medias_semana = {s: [] for s in semanas}

    for oid, info in sorted(dados.items(), key=lambda x: x[1]['nome']):
        ws[f"A{row}"] = info['nome']
        if row % 2 == 0:
            ws[f"A{row}"].fill = PatternFill("solid", start_color=cinza)

        notas_brutas_op = []
        for i, sem in enumerate(semanas):
            col = i + 2
            letra = get_column_letter(col)
            notas = info['semanas'].get(sem, [])
            if notas:
                media = sum(notas) / len(notas)
                ws[f"{letra}{row}"] = f"{int(round(media))}%"
                ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
                ws[f"{letra}{row}"].fill = PatternFill("solid", start_color=cores_semanas[i])
                notas_brutas_op.extend(notas)
                medias_semana[sem].append(media)
            else:
                ws[f"{letra}{row}"] = "—"
                ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
                ws[f"{letra}{row}"].fill = PatternFill("solid", start_color=cores_semanas[i])

        if notas_brutas_op:
            media_op = sum(notas_brutas_op) / len(notas_brutas_op)
            ws[f"J{row}"] = f"{int(round(media_op))}%"
            ws[f"J{row}"].font = Font(bold=True)
            ws[f"J{row}"].alignment = Alignment(horizontal="center")

        row += 1

    ws[f"A{row}"] = "Média Equipe"
    ws[f"A{row}"].font = Font(bold=True, color="2D6A4F")
    ws[f"A{row}"].fill = PatternFill("solid", start_color="D8F3DC")

    for i, sem in enumerate(semanas):
        col = i + 2
        letra = get_column_letter(col)
        if medias_semana[sem]:
            m = sum(medias_semana[sem]) / len(medias_semana[sem])
            ws[f"{letra}{row}"] = f"{int(round(m))}%"
            ws[f"{letra}{row}"].font = Font(bold=True, color="2D6A4F")
            ws[f"{letra}{row}"].fill = PatternFill("solid", start_color="D8F3DC")
            ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")
        else:
            ws[f"{letra}{row}"] = "—"
            ws[f"{letra}{row}"].fill = PatternFill("solid", start_color="D8F3DC")
            ws[f"{letra}{row}"].alignment = Alignment(horizontal="center")

    medias_ops = []
    for oid, info in dados.items():
        todas = [n for notas in info["semanas"].values() for n in notas]
        if todas:
            medias_ops.append(sum(todas) / len(todas))

    if medias_ops:
        media_geral = sum(medias_ops) / len(medias_ops)
        ws[f"J{row}"] = f"{int(round(media_geral))}%"
        ws[f"J{row}"].font = Font(bold=True, color="2D6A4F")
        ws[f"J{row}"].fill = PatternFill("solid", start_color="D8F3DC")
        ws[f"J{row}"].alignment = Alignment(horizontal="center")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ── LOGIN ────────────────────────────────────────
def tela_login():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""<div style="background:#003318;border-radius:16px;padding:40px 32px;
        box-shadow:0 8px 32px rgba(0,0,0,0.3);border:1px solid #005a25">
        <div style="text-align:center;padding:0 0 28px">
            <div style="font-size:28px;font-weight:800;color:#ffffff;margin-bottom:4px">iGreen</div>
            <div style="width:36px;height:2px;background:#00c853;margin:6px auto 10px"></div>
            <p style="color:#5a9a70;font-size:11px;text-transform:uppercase;letter-spacing:2px;margin:0">Monitorias de Qualidade</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px'>USUÁRIO</p>", unsafe_allow_html=True)
        usuario = st.text_input("u", placeholder="seu usuário", label_visibility="collapsed")
        st.markdown("<p style='font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#5a9a70;margin-bottom:4px;margin-top:12px'>SENHA</p>", unsafe_allow_html=True)
        senha = st.text_input("s", type="password", placeholder="••••••••", label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Entrar", use_container_width=True):
            uid = usuario.lower().strip()
            u = USUARIOS.get(uid)
            if u:
                senha_correta = buscar_senha_usuario(uid) or u.get("senha")
                if senha_correta and senha.strip() == senha_correta:
                    st.session_state.usuario = {"id": uid, **u}
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
            else:
                st.error("Usuário ou senha incorretos.")
        st.markdown('<p style="text-align:center;color:#1a4d2e;font-size:11px;margin-top:24px">iGreen Energy © 2026</p>', unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────
def render_sidebar():
    u = st.session_state.usuario
    role_label = 'Administrador' if u['role'] == 'admin' else 'Diretoria' if u['role'] in ['diretor','diretor_upload'] else 'Gestor'
    with st.sidebar:
        st.markdown(
            f"<div style='padding:16px 12px 8px'>"
            f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>"
            f"<div style='width:34px;height:34px;background:#2e7d32;border-radius:8px;"
            f"display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px;color:#fff'>iG</div>"
            f"<div><span style='color:#2e7d32;font-weight:700;font-size:15px'>iGreen</span>"
            f"<span style='color:#1a2e1a;font-weight:700;font-size:15px'> Monitorias</span></div>"
            f"</div></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='margin:0 8px 12px;background:#f0f7f0;border:1px solid #c8e0c8;"
            f"border-radius:8px;padding:10px 12px'>"
            f"<div style='color:#2e7d32;font-weight:700;font-size:14px'>{u['nome']}</div>"
            f"<div style='color:#5a8a5a;font-size:11px'>{role_label}</div>"
            f"</div>", unsafe_allow_html=True)

        anos = get_anos_disponiveis()
        ano = st.selectbox('Ano', anos, label_visibility='collapsed')
        meses = get_todos_meses_ano(int(ano))
        mes_labels = [m.split('-')[0] for m in meses]
        mes_sel = st.selectbox('Mês', mes_labels, index=datetime.now().month - 1, label_visibility='collapsed')
        mes_ano = f'{mes_sel}-{ano}'
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if u['role'] == 'admin':
            pags = ['Monitorias', 'Premiação', 'Operadores', 'Critérios', 'Minha Conta']
        elif u['role'] == 'diretor':
            pags = ['Monitorias', 'Premiação', 'Minha Conta']
        else:
            pags = ['Monitorias', 'Operadores', 'Minha Conta']

        pag = st.radio('Menu', pags, label_visibility='collapsed', index=0)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button('Sair', use_container_width=True):
            del st.session_state.usuario
            st.rerun()
    return mes_ano, pag

# ── OPERADORES ───────────────────────────────────
def pagina_operadores():
    u = st.session_state.usuario
    header_page("Operadores", "Gerencie os operadores da equipe")

    if u['role'] == 'admin':
        eq_opts = list(EQUIPES.keys())
        eq_labels = [f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        eq_sel = st.selectbox("Equipe:", eq_labels, key="op_eq_sel")
        eq = eq_opts[eq_labels.index(eq_sel)]
    else:
        eq = u.get('equipe')

    with st.expander("Cadastrar Novo Operador", expanded=False):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1: nn = st.text_input("Nome", placeholder="Nome completo", key="op_nome_input")
        with c2: np_op = st.checkbox("Pleno", key="op_pleno_input")
        with c3:
            st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
            if st.button("Cadastrar", use_container_width=True, key="op_add_btn"):
                if nn.strip():
                    salvar_operador(eq, nn.strip(), np_op)
                    st.cache_data.clear()
                    st.success(f"✅ {nn} cadastrado!")
                    st.rerun()
                else:
                    st.error("Digite o nome.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    ops = buscar_operadores(eq)
    if not ops:
        st.info("Nenhum operador cadastrado.")
        return

    for op in ops:
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1: nn = st.text_input("n", value=op["nome"], label_visibility="collapsed", key=f"n_{op['_id']}")
        with c2: np = st.checkbox("Pleno", value=op.get("pleno", False), key=f"p_{op['_id']}")
        with c3:
            if st.button("Salvar", key=f"s_{op['_id']}"): atualizar_operador(op["_id"], nn, np); st.cache_data.clear(); st.rerun()
        with c4:
            if st.button("Excluir", key=f"d_{op['_id']}"): excluir_operador(op["_id"]); st.cache_data.clear(); st.rerun()

# ── MONITORIAS ───────────────────────────────────
def pagina_monitorias(ma):
    u = st.session_state.usuario

    if u['role'] == 'diretor':
        pagina_monitorias_diretor(ma)
        return

    if u['role'] == 'admin':
        eq_opts = list(EQUIPES.keys())
        eq_labels = [f"Equipe {EQUIPES[e]['nome']}" for e in eq_opts]
        eq_sel = st.selectbox("Equipe:", eq_labels, key="mon_eq_sel")
        eq = eq_opts[eq_labels.index(eq_sel)]
    else:
        eq = u.get('equipe')

    ops = buscar_operadores(eq)
    if not ops:
        st.warning("Cadastre operadores primeiro.")
        return

    if "mon_op_sel" not in st.session_state:
        st.session_state.mon_op_sel = None

    # ── TELA LISTA DE OPERADORES ──────────────────
    if st.session_state.mon_op_sel is None:
        header_page("Monitorias", f"Equipe {EQUIPES.get(eq, {}).get('nome', '')} · {ma.replace('-', ' ')}")

        # Relatório só gera quando clicar — não carrega automaticamente
        if st.button("⬇️ Baixar Relatório (.xlsx)", key="btn_rel"):
            rel = gerar_relatorio_monitorias(eq, ma)
            if rel:
                st.download_button(
                    "📥 Clique aqui para baixar",
                    rel,
                    file_name=f"monitorias_{eq}_{ma}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_rel_mon"
                )
            else:
                st.info("Nenhuma monitoria registrada neste mês.")

        ultimo = st.session_state.pop("mon_ultimo_salvo", None)
        if ultimo:
            cn_u = "#2e7d32" if ultimo['nota'] >= 80 else "#f57f17" if ultimo['nota'] >= 60 else "#c62828"
            st.markdown(
                f"<div style='background:#f0faf0;border:1px solid #c8e0c8;border-radius:10px;padding:12px 16px;margin-bottom:12px'>"
                f"<div style='color:#2e7d32;font-weight:700'>✓ Monitoria de {ultimo['nome']} salva!</div>"
                f"<div style='color:#1a2e1a;font-size:13px'>Nota: <strong style='color:{cn_u}'>{ultimo['nota']:.0f}%</strong> · Média: <strong>{ultimo['media']:.2f}%</strong> · Pontos: <strong>{ultimo['pontos']}</strong></div>"
                f"</div>", unsafe_allow_html=True)
            st.markdown(f'<a href="data:text/html;base64,{ultimo["b64"]}" download="Mon_{ultimo["nome"].replace(" ","_")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:12px;margin-bottom:12px">⬇ Baixar PDF</a>', unsafe_allow_html=True)

        # Média da equipe
        monts_eq = buscar_monitorias_equipe(eq, ma)
        if monts_eq:
            notas_eq = [float(m['nota']) for m in monts_eq if 'nota' in m]
            if notas_eq:
                me_eq = sum(notas_eq) / len(notas_eq)
                st_txt, st_cor, _ = get_status_media(me_eq)
                st.markdown(
                    f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:10px;"
                    f"padding:12px 20px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center'>"
                    f"<div><div style='color:#3a6a4a;font-size:9px;text-transform:uppercase;letter-spacing:1.5px'>MÉDIA DA EQUIPE — {ma.replace('-',' ').upper()}</div>"
                    f"<div style='color:{st_cor};font-size:22px;font-weight:800;margin-top:2px'>{me_eq:.2f}%</div></div>"
                    f"<div style='color:{st_cor};font-size:13px;font-weight:600'>{st_txt}</div>"
                    f"</div>", unsafe_allow_html=True)

        st.markdown(f"<div style='color:#5a8a5a;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px'>{len(ops)} operadores</div>", unsafe_allow_html=True)

        for i in range(0, len(ops), 4):
            cols = st.columns(4)
            for j, op_item in enumerate(ops[i:i+4]):
                # Calcular média direto das monitorias já buscadas (sem nova query)
                monts_op = [m for m in monts_eq if m.get('opId') == op_item['_id']]
                notas_op = [float(m['nota']) for m in monts_op if 'nota' in m]
                media = round(sum(notas_op) / len(notas_op), 1) if notas_op else 0
                n = len(notas_op)
                st_txt, st_cor, _ = get_status_media(media)
                ini = get_iniciais(op_item["nome"])
                cini = get_cor_inicial(op_item["nome"])
                pontos_op = calc_pontos(media)
                with cols[j]:
                    st.markdown(f"""<div style="background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;
                        padding:16px;text-align:center;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,0.06)">
                        <div style="width:44px;height:44px;background:{cini};border-radius:50%;display:inline-flex;
                        align-items:center;justify-content:center;color:white;font-weight:700;font-size:15px;margin-bottom:8px">{ini}</div>
                        <div style="color:#1a2e1a;font-weight:700;font-size:12px;margin-bottom:4px">{op_item['nome']}{'  ★' if op_item.get('pleno') else ''}</div>
                        <div style="color:{st_cor};font-size:20px;font-weight:800">{round(media)}%</div>
                        <div style="color:#5a8a5a;font-size:10px">{n} monitoria{'s' if n != 1 else ''}</div>
                        <div style="color:#2e7d32;font-size:11px;font-weight:600;margin-top:2px">{pontos_op} pts</div>
                    </div>""", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("+ Nova", key=f"nova_{op_item['_id']}", use_container_width=True):
                            st.session_state.mon_op_sel = op_item
                            st.rerun()
                    with c2:
                        if st.button("Histórico", key=f"hist_{op_item['_id']}", use_container_width=True):
                            st.session_state.mon_op_sel = op_item
                            st.rerun()
        return

    # ── TELA DE NOVA MONITORIA ────────────────────
    op = st.session_state.mon_op_sel
    monts_op_todas = buscar_monitorias_operador(op["_id"])
    monts_op_mes = [m for m in monts_op_todas if m.get("mesAno") == ma]
    notas_todas = [float(m['nota']) for m in monts_op_todas if 'nota' in m]
    media_op = round(sum(notas_todas) / len(notas_todas), 1) if notas_todas else 0
    n_op = len(notas_todas)

    if st.button("← Voltar"):
        st.session_state.mon_op_sel = None
        st.rerun()

    st.markdown(
        f"<div style='background:#e8f5e9;border:1px solid #c8e0c8;border-radius:8px;padding:10px 16px;margin-bottom:12px'>"
        f"<span style='color:#2e7d32;font-weight:700;font-size:15px'>👤 {op['nome']}</span>"
        f"<span style='color:#5a8a5a;font-size:12px;margin-left:12px'>Média geral: {media_op:.0f}% · {n_op} monitoria{'s' if n_op != 1 else ''}</span></div>",
        unsafe_allow_html=True)

    t1, t2 = st.tabs(["Nova Monitoria", "Monitorias do Mês"])

    with t1:
        semanas_usadas = {m.get("semana_mon", "") for m in monts_op_mes}
        semanas_opts = []
        for s in SEMANAS_MONITORIA:
            if s in semanas_usadas:
                semanas_opts.append(f"🔴 {s} — JÁ REGISTRADA")
            else:
                semanas_opts.append(f"✅ {s}")

        semana_sel = st.selectbox("Qual monitoria é esta?", semanas_opts, key="semana_sel")
        semana = SEMANAS_MONITORIA[semanas_opts.index(semana_sel)]
        semana_bloqueada = semana in semanas_usadas
        sk_salvo = f"mon_salvo_{op['_id']}_{semana}_{ma}"

        # ── JÁ SALVOU — mostra só resultado + PDF ──
        if st.session_state.get(sk_salvo):
            salvo = st.session_state[sk_salvo]
            cn2 = "#2e7d32" if salvo['nota'] >= 80 else "#f57f17" if salvo['nota'] >= 60 else "#c62828"
            st.markdown(
                f"<div style='background:#f0faf0;border:2px solid #2e7d32;border-radius:16px;"
                f"padding:32px;text-align:center;margin:16px 0'>"
                f"<div style='color:#2e7d32;font-size:13px;font-weight:600;text-transform:uppercase;"
                f"letter-spacing:1px;margin-bottom:8px'>✓ Monitoria salva com sucesso!</div>"
                f"<div style='color:{cn2};font-size:64px;font-weight:800;line-height:1;margin-bottom:8px'>{salvo['nota']:.0f}%</div>"
                f"<div style='color:#1a2e1a;font-size:14px;margin-bottom:4px'>Média: <strong>{salvo['media']:.2f}%</strong></div>"
                f"<div style='color:#2e7d32;font-size:14px;font-weight:700;margin-bottom:24px'>Pontuação: {salvo['pontos']} pts</div>"
                f"</div>", unsafe_allow_html=True)
            st.markdown(
                f'<a href="data:text/html;base64,{salvo["b64"]}" '
                f'download="Monitoria_{salvo["nome"].replace(" ","_")}_{salvo["prot"]}.html" '
                f'style="display:block;text-align:center;background:#1a3a1a;color:#a0c4a0;'
                f'border:1px solid #2a4a2a;padding:14px 24px;border-radius:8px;'
                f'text-decoration:none;font-weight:600;font-size:14px;margin-bottom:12px">'
                f'⬇ Baixar PDF da Monitoria</a>', unsafe_allow_html=True)
            if st.button("← Voltar para a equipe", use_container_width=True, key="btn_concluir_mon"):
                ultimo = st.session_state.pop(sk_salvo, None)
                st.session_state.mon_op_sel = None
                if ultimo:
                    st.session_state["mon_ultimo_salvo"] = ultimo
                st.rerun()

        # ── AINDA NÃO SALVOU — mostra formulário ──
        else:
            if semana_bloqueada:
                st.error(f"⛔ A **{semana}** já foi registrada para {op['nome']} em {ma.replace('-',' ')}.")

            prot = st.text_input("Protocolo da Ligação", placeholder="Ex: 20260520-001", key="prot_input")
            obs = st.text_area("Observações", placeholder="Anotações...", height=70, key="obs_input")
            st.markdown("---")

            crits_usar = get_criterios()
            erros_usar = get_erros_criticos()

            # Erros críticos
            st.markdown("<p style='color:#c62828;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>ERROS CRÍTICOS — Qualquer um zera a monitoria</p>", unsafe_allow_html=True)
            erros_m = []
            c1, c2 = st.columns(2)
            for i, ec in enumerate(erros_usar):
                with (c1 if i % 2 == 0 else c2):
                    if st.checkbox(f"{ec['nome']}", key=f"ec_{ec['id']}", help=ec['desc']):
                        erros_m.append(ec)

            st.markdown("---")
            zerada = len(erros_m) > 0
            crits_r = []
            nota = 0 if zerada else 100

            if zerada:
                st.error("MONITORIA ZERADA — Erro crítico marcado!")
                for c in crits_usar:
                    crits_r.append({**c, "passou": False})
            else:
                st.markdown("<p style='color:#e53935;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>CRITÉRIOS — MARQUE O QUE NÃO FOI FEITO</p>", unsafe_allow_html=True)
                for crit in crits_usar:
                    c1, c2 = st.columns([8, 1])
                    with c1:
                        nao_passou = st.checkbox(f"{crit['num']} {crit['nome']}", key=f"cr_{crit['id']}", value=False)
                    with c2:
                        st.markdown(f"<div style='padding-top:6px;color:#e53935;font-size:12px;font-weight:600;text-align:right'>−{crit['peso']} pts</div>", unsafe_allow_html=True)
                    if crit.get('itens'):
                        for it in crit['itens']:
                            cor_it = "#f87171" if "obrigatório" in it.lower() or "!" in it else "#34d399"
                            st.markdown(f"<div style='padding:3px 0 3px 24px;font-size:12px;color:{cor_it};line-height:1.5'>• {it}</div>", unsafe_allow_html=True)
                    passou = not nao_passou
                    if not passou:
                        nota -= crit["peso"]
                    crits_r.append({**crit, "passou": passou})

            nota = max(0, nota)
            pontos_perdidos = 100 - nota
            cn = "#2e7d32" if nota >= 80 else "#f57f17" if nota >= 60 else "#c62828"
            st.markdown(
                f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:10px;"
                f"padding:14px 20px;margin-top:16px;display:flex;justify-content:space-between;align-items:center'>"
                f"<div><div style='color:#5a8a5a;font-size:11px'>Pontuação final (máx. 100 pts)</div>"
                f"<div style='color:#5a8a5a;font-size:11px'>Pontos perdidos: {pontos_perdidos}</div></div>"
                f"<div style='color:{cn};font-size:36px;font-weight:800'>{round(nota)}</div>"
                f"</div>", unsafe_allow_html=True)

            if st.button("💾 Salvar Monitoria", use_container_width=True, key="btn_salvar_mon", disabled=semana_bloqueada):
                if not prot.strip():
                    st.error("Preencha o Protocolo da Ligação!")
                else:
                    salvar_monitoria(eq, op["_id"], op["nome"], prot, obs, crits_r, erros_m, nota, ma, semana=semana)
                    # Recalcular média com a nova monitoria incluída
                    notas_novas = [float(m['nota']) for m in buscar_monitorias_operador(op["_id"]) if 'nota' in m]
                    mm = round(sum(notas_novas) / len(notas_novas), 1) if notas_novas else nota
                    nm = len(notas_novas)
                    html = gerar_pdf_monitoria(op["nome"], prot, obs, crits_r, erros_m, nota, mm, nm, ma)
                    b64 = base64.b64encode(html.encode()).decode()
                    st.session_state[sk_salvo] = {
                        "nome": op["nome"], "nota": nota,
                        "media": mm, "pontos": calc_pontos(mm),
                        "b64": b64, "prot": prot
                    }
                    st.rerun()

    with t2:
        monts2 = buscar_monitorias_operador(op["_id"])
        monts2 = [m for m in monts2 if m.get("mesAno") == ma]
        if not monts2:
            st.info(f"Nenhuma monitoria para {op['nome']} em {ma.replace('-',' ')}.")
        else:
            ordem_semanas = {s: i for i, s in enumerate(SEMANAS_MONITORIA)}
            monts2 = sorted(monts2, key=lambda x: ordem_semanas.get(x.get("semana_mon", ""), 99))
            for m in monts2:
                nm = float(m.get("nota", 0))
                cm = "#2e7d32" if nm >= 80 else "#f57f17" if nm >= 60 else "#c62828"
                st.markdown(
                    f"<div style='background:#f8fdf8;border:1px solid #c8e0c8;border-radius:10px;"
                    f"padding:14px 18px;margin-bottom:8px;border-left:3px solid {cm}'>"
                    f"<div style='color:#1a2e1a;font-weight:600'>{m.get('semana_mon','—')}</div>"
                    f"<div style='color:#5a8a5a;font-size:11px'>Protocolo: {m.get('protocolo','—')} · {str(m.get('criadoEm',''))[:10]}</div>"
                    f"<div style='color:{cm};font-size:18px;font-weight:800'>{int(nm)}%</div></div>", unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    for c in m.get("criterios", []):
                        passou = c.get("passou", True)
                        cc = "#2e7d32" if passou else "#c62828"
                        st.markdown(
                            f"<div style='display:flex;justify-content:space-between;padding:6px 12px;"
                            f"background:#f0f7f0;border-radius:6px;margin-bottom:4px;border-left:3px solid {cc}'>"
                            f"<span style='color:#1a2e1a;font-size:12px'>{c.get('num','')} {c.get('nome','')}</span>"
                            f"<span style='color:{cc};font-weight:600;font-size:12px'>{'Passou' if passou else 'Não passou'}</span></div>", unsafe_allow_html=True)
                    if m.get("observacao"):
                        st.markdown(f"<div style='padding:8px 12px;background:#f0f7f0;border-radius:6px;border-left:3px solid #5a8a5a;color:#2d4a2d;font-size:12px'><strong>Obs:</strong> {m['observacao']}</div>", unsafe_allow_html=True)
                    mm2, nm2 = calc_media_operador(op["_id"], ma)
                    hp = gerar_pdf_monitoria(op["nome"], m.get("protocolo", ""), m.get("observacao", ""), m.get("criterios", []), m.get("errosCriticos", []), nm, mm2, nm2, ma)
                    b64h = base64.b64encode(hp.encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64h}" download="Mon_{op["nome"].replace(" ","_")}.html" style="display:inline-block;background:#1a3a1a;color:#a0c4a0;border:1px solid #2a4a2a;padding:5px 12px;border-radius:5px;text-decoration:none;font-size:12px;margin-top:6px">⬇ Baixar PDF</a>', unsafe_allow_html=True)
                    st.markdown("---")
                    if st.button("Excluir", key=f"del_op_{m['_id']}"):
                        excluir_monitoria(m["_id"])
                        st.rerun()

def pagina_monitorias_diretor(ma):
    header_page("Monitorias", f"Visão Geral · {ma.replace('-',' ')}")
    if "dir_op_sel" not in st.session_state: st.session_state.dir_op_sel = None
    if "dir_eq_sel" not in st.session_state: st.session_state.dir_eq_sel = None

    if st.session_state.dir_op_sel:
        op = st.session_state.dir_op_sel
        eq = st.session_state.dir_eq_sel
        media_op, n_op = calc_media_operador(op["_id"], ma)
        st_txt, st_cor, _ = get_status_media(media_op)
        if st.button("← Voltar"):
            st.session_state.dir_op_sel = None
            st.session_state.dir_eq_sel = None
            st.rerun()
        st.markdown(f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:12px;padding:16px 20px;margin-bottom:16px'>"
                    f"<div style='color:#1a2e1a;font-weight:700;font-size:16px'>{op['nome']}</div>"
                    f"<div style='color:#5a8a5a;font-size:12px'>Equipe {EQUIPES.get(eq,{}).get('nome','—')} · {ma.replace('-',' ')} · Média: <strong style='color:{st_cor}'>{media_op:.2f}%</strong></div></div>", unsafe_allow_html=True)
        monts_op = [m for m in buscar_monitorias_equipe(eq, ma) if m["opId"] == op["_id"]]
        if not monts_op:
            st.info("Nenhuma monitoria registrada neste mês.")
        else:
            for m in monts_op:
                nm = float(m.get("nota", 0))
                cm = "#2e7d32" if nm >= 80 else "#f57f17" if nm >= 60 else "#c62828"
                st.markdown(f"<div style='background:#f8fdf8;border:1px solid #c8e0c8;border-radius:10px;padding:14px 18px;margin-bottom:8px;border-left:3px solid {cm}'>"
                            f"<div style='color:#1a2e1a;font-weight:600'>{m.get('semana_mon','—')}</div>"
                            f"<div style='color:#5a8a5a;font-size:11px'>Protocolo: {m.get('protocolo','—')}</div>"
                            f"<div style='color:{cm};font-size:18px;font-weight:800'>{nm:.0f}%</div></div>", unsafe_allow_html=True)
                with st.expander("Ver detalhes"):
                    for c in m.get("criterios", []):
                        passou = c.get("passou", True)
                        cc = "#2e7d32" if passou else "#c62828"
                        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:6px 12px;background:#f0f7f0;border-radius:6px;margin-bottom:4px;border-left:3px solid {cc}'><span style='color:#1a2e1a;font-size:12px'>{c.get('num','')} {c.get('nome','')}</span><span style='color:{cc};font-weight:600;font-size:12px'>{'Passou' if passou else 'Não passou'}</span></div>", unsafe_allow_html=True)
        return

    linhas_eq = ""
    todas_medias = []
    for eq_pre in ["danilo", "deborah", "tamires", "luciano", "metcool"]:
        ops_pre = buscar_operadores(eq_pre)
        medias_pre = [calc_media_operador(op["_id"], ma)[0] for op in ops_pre if calc_media_operador(op["_id"], ma)[1] > 0]
        if medias_pre:
            me_pre = sum(medias_pre) / len(medias_pre)
            nome_eq = EQUIPES.get(eq_pre, {}).get("nome", eq_pre)
            cor_me = "#2e7d32" if me_pre >= 80 else "#f57f17" if me_pre >= 60 else "#c62828"
            linhas_eq += f"<div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #e8f0e8'><span style='color:#2d4a2d;font-size:13px;font-weight:500'>{nome_eq}</span><span style='color:{cor_me};font-size:15px;font-weight:700'>{me_pre:.2f}%</span></div>"
            todas_medias.append(me_pre)

    if todas_medias:
        mg = sum(todas_medias) / len(todas_medias)
        cor_mg = "#2e7d32" if mg >= 80 else "#f57f17" if mg >= 60 else "#c62828"
        linhas_eq += f"<div style='border-top:1px solid #c8e0c8;margin-top:6px;padding-top:8px;display:flex;justify-content:space-between;align-items:center'><span style='color:#2d4a2d;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px'>Média Geral</span><span style='color:{cor_mg};font-size:22px;font-weight:800'>{mg:.2f}%</span></div>"
        st.markdown(f"<div style='background:#ffffff;border:1px solid #c8e0c8;border-radius:12px;padding:16px 24px;margin-bottom:20px;border-left:4px solid #2e7d32'>{linhas_eq}</div>", unsafe_allow_html=True)

    for eq in list(EQUIPES.keys()) + ["luciano", "metcool"]:
        ops = buscar_operadores(eq)
        if not ops: continue
        monts = buscar_monitorias_equipe(eq, ma)
        if not monts: continue
        medias = {op["nome"]: (op, calc_media_operador(op["_id"], ma)) for op in ops}
        medias = {k: v for k, v in medias.items() if v[1][1] > 0}
        if not medias: continue
        me = sum(v[1][0] for v in medias.values()) / len(medias)
        cor = "#2e7d32" if me >= 80 else "#f57f17" if me >= 60 else "#c62828"
        st.markdown(f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:12px;padding:16px 20px;margin-bottom:8px;border-left:3px solid #2e7d32'><div style='display:flex;justify-content:space-between;align-items:center'><div style='font-size:15px;font-weight:700;color:#1a2e1a'>Equipe {EQUIPES[eq]['nome']}</div><div style='text-align:right'><div style='color:#5a8a5a;font-size:10px;text-transform:uppercase'>MÉDIA</div><div style='color:{cor};font-size:24px;font-weight:800'>{me:.2f}%</div></div></div></div>", unsafe_allow_html=True)
        cols_op = st.columns(4)
        for idx_op, (nome, (op_obj, (media, n))) in enumerate(sorted(medias.items(), key=lambda x: -x[1][1][0])):
            st_txt, st_cor, _ = get_status_media(media)
            with cols_op[idx_op % 4]:
                st.markdown(f"<div style='background:#ffffff;border:1px solid #c8e0c8;border-radius:10px;padding:12px;text-align:center;margin-bottom:8px'><div style='color:#1a2e1a;font-weight:600;font-size:12px'>{nome}</div><div style='color:{st_cor};font-size:18px;font-weight:800'>{media:.2f}%</div><div style='color:#5a8a5a;font-size:10px'>{n} monitoria{'s' if n!=1 else ''}</div></div>", unsafe_allow_html=True)
                if st.button("Ver detalhes", key=f"dir_op_{op_obj['_id']}", use_container_width=True):
                    st.session_state.dir_op_sel = op_obj
                    st.session_state.dir_eq_sel = eq
                    st.rerun()
        st.markdown("---")

# ── CRITÉRIOS ────────────────────────────────────
def pagina_criterios():
    header_page("Critérios de Monitoria", "Configure os critérios de avaliação")
    crits = get_criterios()
    erros = get_erros_criticos()
    t1, t2 = st.tabs(["Critérios de Avaliação", "Erros Críticos"])
    with t1:
        st.markdown("**Distribuição: 100 pontos totais. Alterações valem apenas para novas monitorias.**")
        total_peso = sum(c['peso'] for c in crits)
        st.markdown(f"<div style='background:#f0f7f0;border:1px solid #c8e0c8;border-radius:8px;padding:10px 16px;margin-bottom:16px'>"
                    f"<span style='color:#2e7d32;font-weight:700'>Total configurado: {total_peso} pts</span>"
                    f"{'  ✅' if total_peso == 100 else '  ⚠️ Deve somar 100'}</div>", unsafe_allow_html=True)
        st.markdown("---")
        ce = []
        for i, c in enumerate(crits):
            with st.expander(f"{c['num']} {c['nome']} — {c['peso']} pts", expanded=False):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1: nm = st.text_input("Nome", value=c["nome"], key=f"cn_{i}")
                with col2: ps = st.number_input("Peso", min_value=1, max_value=100, value=int(c["peso"]), key=f"cp_{i}")
                with col3: ob = st.checkbox("Obrigatório", value=c.get("obrigatorio", False), key=f"co_{i}")
                it = st.text_area("Itens (um por linha)", value="\n".join(c.get("itens", [])), height=100, key=f"ci_{i}")
                ce.append({"id": c["id"], "num": c["num"], "nome": nm, "peso": ps, "obrigatorio": ob,
                           "itens": [x.strip() for x in it.split("\n") if x.strip()]})
        st.markdown("---")
        if st.button("Salvar Critérios", use_container_width=True):
            salvar_criterios(ce)
            st.success("Critérios salvos!")
            st.rerun()
    with t2:
        st.markdown("**Erros que zeram a monitoria automaticamente.**")
        st.markdown("---")
        ee = []
        for i, e in enumerate(erros):
            col1, col2 = st.columns([2, 3])
            with col1: ne = st.text_input("Nome", value=e["nome"], key=f"en_{i}")
            with col2: de = st.text_input("Descrição", value=e["desc"], key=f"ed_{i}")
            ee.append({"id": e["id"], "nome": ne, "desc": de})
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Salvar Erros Críticos", use_container_width=True):
                salvar_erros_criticos(ee)
                st.success("Salvo!")
                st.rerun()
        with col2:
            if st.button("Adicionar Erro", use_container_width=True):
                ee.append({"id": f"e{len(erros)+1}", "nome": "Novo erro", "desc": "Descrição"})
                salvar_erros_criticos(ee)
                st.rerun()

# ── PREMIAÇÃO — BANCO ────────────────────────────
def salvar_premiacao(ma, dados):
    get_db().configuracoes.update_one(
        {"_id": f"premiacao_{ma}"},
        {"$set": {"_id": f"premiacao_{ma}", "mesAno": ma, "dados": dados, "atualizadoEm": datetime.now()}},
        upsert=True
    )

def buscar_premiacao(ma):
    try:
        doc = get_db().configuracoes.find_one({"_id": f"premiacao_{ma}"})
        if doc:
            return doc.get("dados")
    except:
        pass
    return None

# ── PREMIAÇÃO — PÁGINA ────────────────────────────
def pagina_premiacao(ma):
    import streamlit.components.v1 as components
    import os
    header_page("Premiação", f"Cálculo mensal · {ma.replace('-', ' ')}")
    st.markdown(
        "<style>iframe{width:100%!important;min-width:100%!important;border:none!important}"
        ".block-container{padding:1rem!important;max-width:100%!important}</style>",
        unsafe_allow_html=True
    )
    # HTML inline
    _html = PREMIACAO_HTML
    components.html(_html, height=2600, scrolling=True)


# ── MINHA CONTA ──────────────────────────────────
def pagina_minha_conta():
    u = st.session_state.usuario
    header_page('Minha Conta', u['nome'])
    st.markdown("### 🔒 Alterar Senha")
    sa = st.text_input('Senha atual', type='password', placeholder='senha atual')
    sn = st.text_input('Nova senha', type='password', placeholder='mín. 8 caracteres')
    sc2 = st.text_input('Confirmar senha', type='password', placeholder='repita a nova senha')
    if st.button('Salvar Senha', use_container_width=True):
        uid = u['id']
        sc = buscar_senha_usuario(uid) or u.get('senha')
        if not sa: st.error('Digite a senha atual.')
        elif sa != sc: st.error('Senha atual incorreta.')
        elif len(sn) < 8: st.error('Mínimo 8 caracteres.')
        elif sn != sc2: st.error('Confirmação não confere.')
        else:
            salvar_senha_usuario(uid, sn)
            st.success('✅ Senha alterada com sucesso!')

# ── MAIN ─────────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return

    # Migração automática de equipes — roda uma vez por deploy (v2)
    if st.session_state.get('equipes_migradas') != 'v3':
        st.session_state.equipes_migradas = 'v3'
        migrar_operadores()
        st.cache_data.clear()

    ma, pag = render_sidebar()
    u = st.session_state.usuario

    if 'Monitorias' in pag:
        pagina_monitorias(ma)
    elif 'Premiação' in pag:
        pagina_premiacao(ma)
    elif 'Operadores' in pag:
        pagina_operadores()
    elif 'Critérios' in pag and u['role'] == 'admin':
        pagina_criterios()
    elif 'Minha Conta' in pag:
        pagina_minha_conta()

if __name__ == "__main__":
    main()
# ── MINHA CONTA ──────────────────────────────────
def pagina_minha_conta():
    u = st.session_state.usuario
    header_page('Minha Conta', u['nome'])
    st.markdown("### 🔒 Alterar Senha")
    sa = st.text_input('Senha atual', type='password', placeholder='senha atual')
    sn = st.text_input('Nova senha', type='password', placeholder='mín. 8 caracteres')
    sc2 = st.text_input('Confirmar senha', type='password', placeholder='repita a nova senha')
    if st.button('Salvar Senha', use_container_width=True):
        uid = u['id']
        sc = buscar_senha_usuario(uid) or u.get('senha')
        if not sa: st.error('Digite a senha atual.')
        elif sa != sc: st.error('Senha atual incorreta.')
        elif len(sn) < 8: st.error('Mínimo 8 caracteres.')
        elif sn != sc2: st.error('Confirmação não confere.')
        else:
            salvar_senha_usuario(uid, sn)
            st.success('✅ Senha alterada com sucesso!')

# ── MAIN ─────────────────────────────────────────
def main():
    if "usuario" not in st.session_state:
        tela_login()
        return

    # Migração automática de equipes — roda uma vez por deploy (v2)
    if st.session_state.get('equipes_migradas') != 'v3':
        st.session_state.equipes_migradas = 'v3'
        migrar_operadores()
        st.cache_data.clear()

    ma, pag = render_sidebar()
    u = st.session_state.usuario

    if 'Monitorias' in pag:
        pagina_monitorias(ma)
    elif 'Premiação' in pag:
        pagina_premiacao(ma)
    elif 'Operadores' in pag:
        pagina_operadores()
    elif 'Critérios' in pag and u['role'] == 'admin':
        pagina_criterios()
    elif 'Minha Conta' in pag:
        pagina_minha_conta()

if __name__ == "__main__":
    main()
