import requests

url = "https://dpgwint-dev.ghc.org/epic/interconnect/PharmacyServices"
# headers = {'content-type': 'application/soap+xml'}
# headers = {'content-type': 'text/xml'}
headers = {"Host": "www.webservicex.net",
           "Content-Type": "text/xml; charset=UTF-8"}

body = """<soapenv:Envelope xmlns:epic="Epic.Clinical.Pharmacy.WebServices2015" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Header>
      <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
         <wsse:UsernameToken wsu:Id="UsernameToken-67849DB7B586A71A7916990275972322">
            <wsse:Username>svcivrwillowdev</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">W!110w62</wsse:Password>
         </wsse:UsernameToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <epic:GetVersion>
         <!--Optional:-->
         <epic:systemId>IVR_Refill</epic:systemId>
      </epic:GetVersion>
   </soapenv:Body>
</soapenv:Envelope>"""

response = (requests.request("GET",url=url,data=body,headers=headers,verify=False))
print(response)

