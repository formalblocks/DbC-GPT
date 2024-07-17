import openai, os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPEN_AI_KEY')

if api_key is None:
    raise ValueError("API key is not set. Please check your .env file.")

# Set your OpenAI API key
openai.api_key = api_key

def fetch_and_save_thread(thread_id, filename):
    try:
        # Use the new API endpoint to retrieve the chat completion
        response = openai.beta.threads.messages.list(thread_id=thread_id)

        # Write the response to a txt file
        with open(filename, 'w') as file:
            file.write(str(response))

        print(f"Response saved to {filename}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

thread_ids_1155_1155_721_20 = ['thread_wioiAoiEA829BZp1oZ7hbYhb', 'thread_lRDDCWxVmPP6IraolWzMjSvt', 'thread_raVLfnCg2OKPfjE4cAMBvEU3', 'thread_ZNYd5JA4HcsJDhDbVHSygGSG', 'thread_8qNsPCO8J4ZjE6KApFpgoXlC', 'thread_CQmCt26fesfQKonChvBNrXXm', 'thread_sOrytF204Sm0vr58U5LTcntI', 'thread_w3bVaKAy9jbdyLi9msAe4dDO', 'thread_BBqxsfzd8orIImxH8ZAxR9Y3', 'thread_PSJeU5Vg8ADrTJHuXJ2Ur1tY']

thread_ids_1155_1155_721 = ['thread_MmKUc8aEVCyA4h9ISDYeUElx', 'thread_PbbvnfoqpD8RDeIC4J2wuagY', 'thread_StSLttYk9A4DD8H7pKvfBYG9', 'thread_s6c5XK7UYiKqUIV65eT9b2RM', 'thread_lMHt0rQcLjj5aZGgiaU5pMxk', 'thread_XD7CU3Tvm0zfIn9zw3qYcMn9', 'thread_Ho3H9MDwWeigkMgtA6ycZdih', 'thread_lLCEM6an8iJeTA1N9nbOigFt', 'thread_XE9TyLVfxqmGPLph41hiPmhF', 'thread_BooFHij1DSsVZCmtptJJNrdm']

thread_ids_1155_1155_20 = ['thread_zuCpLYLzRp30idyccgbzLNuR', 'thread_0CFfCzovmx1gQBnQ14nwOL6P', 'thread_l7luIKTUOfFeAjJ6GskP9nQV', 'thread_RsRdsSdbjBnC0oKD1hDrnmgH', 'thread_vakN0eTVYPhUHNm0JDfYudFq', 'thread_a0OZJpqDfPG9fnS3W2wk1xIg', 'thread_Cv7666md4aqUylEvpyTLFI8Y', 'thread_RS2QrBoSwn7QRUIdlOHfarIY', 'thread_MX9ysarAPgY20HjukJWzX7eN', 'thread_Fu3a9giLTshTbqzuf6lQCKqg']

thread_ids_1155_20_721 = ['thread_EEbh6Rmr6DHudRQUeEpaJ2DJ', 'thread_cGOyTQhyiIZ0cDRxPm6OlhT2', 'thread_r7Ew9OqC8V9XxAlVK24zgleA', 'thread_a5E1Sei1D1cjhNbOH5BzwU7J', 'thread_dA7YNoV3laaYFrmDpMwvXpx1', 'thread_zQyXQzwzscKh662PJsi70qO1', 'thread_eTXWckOUShvqsgW8KP4RgNcE', 'thread_c5ZZjnr8JrAboy6boHKZ8tmN', 'thread_6DWRa2hoxscB06cxmHtIMFov', 'thread_N48NYvvaCwUNIOuJPlvZewwH']

thread_ids_1155_721 = ['thread_JdRZUdIFLzVzJSxrBWUiYsee', 'thread_u2Y8R2W0OB9lY8L3cCAL0ozD', 'thread_ClyujEPJDMD9kCaPQ06jZLFU', 'thread_JUcwQCTWRsFFBSsCyrvCRnV2', 'thread_9c6h3IDlE9cV1IJ0DOJ1Hu6O', 'thread_Ifw8i2r9WwYOEySEQvClQo1T', 'thread_HdHjKswoFVoc37fdy2bLLQ08', 'thread_zJyo3jBVJmmFYNkgXYWxRRLX', 'thread_XDUtxE7jmFoS1NoCdZ7udfxB', 'thread_lXmh2PY2OTNUGpwNnEFT1yhy']

thread_ids_1155 = ['thread_Rq0uFovhxGNCfuLWzK6KRvG2', 'thread_tQBbkjr3mpFoNYwJ6Mu4aErk', 'thread_1M6sHhQfFrzuHZn0P2f0wxC8', 'thread_6RYhM2Lj0ImYhkSDjUaoBfEJ', 'thread_I7hvuRnu0RIrhTBIxNKCg7nZ', 'thread_YO3ZCHuHQk3g8WbfdSNWTBHc', 'thread_0ra6ya0jWrmkBljIbMB7kj4T', 'thread_VIjF392rv3n83eUmHpGgOonF', 'thread_5DJhGmxTElP6VYjV4tV4wQvJ', 'thread_rQMbEYegkX5e2VDDXyuixoUV']

thread_ids_1155_1155 = ['thread_4BymahcrkJAI97DjPVUfsh8D', 'thread_gwNpEWwkCBPeZTHHl5WehwpM', 'thread_9fuBXBgB7S6mcLr16jk27sts', 'thread_Io2J5tkCtT3Cmn7qmDJRoCIn', 'thread_AWPp1NW9I134fe5eM69xXexo', 'thread_kL206WhtYGT6TPLnd4F9U6jk', 'thread_EYVm0IZgZ1NmBfEMr6cRhzn8', 'thread_dvrbZwcs3I5zj8TfCpgq944b', 'thread_CWnhTR78zYkIPqVReN2oZYRl', 'thread_62Mivcc23fWBUutGsxDbxX0c']

thread_ids_1155_20 = ['thread_CwHayrzakveo9fecnWzAAJ8w', 'thread_JuOUEfhUm9MlS0Q6U4TPu10h', 'thread_cvzRqM1GlKKXe3EEEwyL3QR3', 'thread_VC06zgBji4iknSUeSfsgdSUB', 'thread_FKZZbts7tZbSBtSf5Gdwwsvx', 'thread_pF3pJlS9z57u1ZsN38kcFOMA', 'thread_1OBsf3evwY6lZUwHQyHNSpjZ', 'thread_lOGeuSsckF7YiDluW2UHvvT2']

thread_ids_721_721_1155 = ['thread_LFXU5YY94j6XcpdurxxQ07qE', 'thread_emMdox5mKowi9NEIqzwGo5Sz', 'thread_Dfwfa28yr1TeaY7jRIdCSk8Y', 'thread_uaJnyBrfn2zqOgvqjwHMGTzC', 'thread_IgZKos6D3gEFOPBhCsw6c21T', 'thread_e3sK52YgVS8GDwpwOt6iTMuX', 'thread_95X14JR8Abyn0Y2u9DjU7oEd', 'thread_N7oeCswF7zUxIHeB5DtMeDfm', 'thread_5x0aNfAeUc4tBjxFYTUckaKi', 'thread_oU94s9E9e3ieOiUIHnEevaZc']

thread_ids_721_721_20_1155 = ['thread_qYkAvOmQcFC9LxtsNujPH3xa', 'thread_gxqrQeW4lE4YOXl2ZROzuw0N', 'thread_uY8if4pi0YcYIyoi7MkLjvtR', 'thread_wSOqdFTA9LzzEaf5Ps6Ubd3Y', 'thread_ErHqN26scvTgCZHZMNqq1Dd2', 'thread_VEm0J5e5parSPMj7HM3PoxZp', 'thread_aib91EGAW02MzUJy4VaY2bx4', 'thread_GAzntr28rIj17nEyxBcq0ai3', 'thread_LJs40x9jkotach9VWQzsuItk', 'thread_oAIoBWTNze023BX3k7hb6Gt8']

threads_ids_20_20_721_1155 = ['thread_0KRljF4oPw129e0aFVDZuP3o', 'thread_7vnlpBY2DZ8BitViI9puz99C', 'thread_x3ZP9SoPumJDr6vMOW6kNSEW', 'thread_6vRJp3eLkZiBLBpGgkYUcGIk', 'thread_wTqMg6wmrk2zxtxcPwLj1fcL', 'thread_rN1Ogc8zMLvmPKOjIU4LJaax', 'thread_f2wwZbHzgGadxfXhJZAtj38A', 'thread_NbfeCdvtlJyNcI5FHaz76jzw', 'thread_cqCYKny6AL7ds7f55UNrZRwe', 'thread_lraeamd8Ht8s4Gqoc3LiYLB3']

threads_ids_20_20_1155 = ['thread_48bEzrBfejFEOa8pTnAGC20A', 'thread_o5WC1UQcVr3RHioQFuYTGfi5', 'thread_FAViWEagsUaJzS80zjNSX4V7', 'thread_PSY7Cxjv7NAc1aPt83sX9SH7', 'thread_tIFfxCBrbZoqrXpgFeVjTNbP', 'thread_GfLWbjNcVoP15yoxslLWbvbF', 'thread_lAPM69idpKTzdr5IAuv2GUO3', 'thread_qScfkjHcq4VqUwG9w4O88zdI', 'thread_G07lLJ7tLpKEHrFoD7M6EFa2', 'thread_223ySdRuaDMlGYBA5jQDqLZj']

threads_ids_721_721_20 = ['thread_Okn7MB31wBc1xLnUaqak5rp5', 'thread_cJBJ01q6rCbHlGAu5IwwNpBV', 'thread_ocNX7ZNhjmTeJs482dDf3QO2', 'thread_px32Rr8BYfDswUhN6Gm8pgTX', 'thread_z8s6kQzIidjw636lDcZnTPZq', 'thread_wnkmaEZVfsZC7fhaAIExo7cR', 'thread_bps2JLJl5uP6yEn7Zd8Qa0fr', 'thread_P4RAGEI9A7IYF2TKCweGi4dC', 'thread_zLhdqKd6LvTq3ot3hEJ9sOby', 'thread_KavgjdudOkILvtl9BIl7J3wR']

threads_ids_20_20_721 = ['thread_GD009Y52jvqaUfLlhk9RRpgf', 'thread_Sqp2JeMKf2AdWn0KRlrtXgZ4', 'thread_4hgbETouzHfyJ40BM9zO4qdf', 'thread_WhMGeNtTaCRNNsc1j2ZSU7tl', 'thread_92TGSGOcibsVqZiyVbDc6Y4g', 'thread_Ai95IfCLasSVxI4mtSyUGmBb', 'thread_Ok6x1kqmpAjNN9pcAUjrn9HP', 'thread_21lm1zrOS6eyQ0LcOKVKWeDe', 'thread_EmuetjwIlciW6RiCPNxBapXY', 'thread_t2TLCjXZu1fOfZfeJWHg5rI3']

threads_ids_721_1155 = ['thread_l4wMEQhYMPYAeHcrooz6dk2v', 'thread_NHhytidAetdeNIv35cUT1whz', 'thread_fELOj7CnWIN1u0vR9etfiuM3', 'thread_MIu6Cy3eBrtxfnCtWm4RH7jS', 'thread_yw2bBWuuRKYQcQHhaPJUyXw7', 'thread_mYEBwoBfIx6Hpm6BlVNGypsj', '']

threads_ids_20_721 = ['thread_xZZiPfAIWPPUGy3lpYKKieLD', 'thread_cUuQuHRDar6ZkYPogexDmd1o', 'thread_aQMjTIQGXws0juHFfKHKrdcG', 'thread_yt0yab3zRYulIs6sMnIYKA4y', 'thread_pZDr9bEh8J8KRpJyhifQANjS', 'thread_sa6wwaSq5vxglPnhSbRT99bw', 'thread_vfu9t1NoixggkFd8TpAZWXn1', 'thread_giE9zB4OHFfb3tGeoBCfQVB7', 'thread_QQdT7JqmSVRoLqYVR2oM5xJg', 'thread_vnHmjHDcLSDmwfVgSs5zYVfP']

threads_ids_20 = ['thread_8UCq1mjexUuCMLmhm63j4T8q', 'thread_hwcaBg8G8FIrIlIsgqHEEkkb', 'thread_t6GShmihuUlalHFmw8XbhfJE', 'thread_h3iXDgvZS1UpxZY8h9QbRojW', 'thread_EyftMHcWZ0BXy7pDN6GksHPI', 'thread_Kr6OmZnucZFyJvKhparISwyY', 'thread_fMATlrSKymKOLxZatQldrDA9', 'thread_TQxHLvzeyVZzYfsP1ssbGdCf', 'thread_qvtz5XX5CHeVw6puKYc1NnyK', 'thread_L61wK9V7pkBAddOz8sGejuYh']

threads_ids_721_20 = ['thread_C05u3BPnERbxQvGrnJIPd49a', 'thread_4ioPSeugzGwdD2jfT0qUvbNx', 'thread_WDILJejrDsTeQs03DOhKbeQq', 'thread_WLZc7aRGNU1rGwGZCbK1PIhi', 'thread_F5RoGul2IqaNp0csBCv4Hwhj', 'thread_HCsmvzkTEUjaSo5qdk51RZbQ', 'thread_NPZOcYARO9RKrJZAcSJN18bS', 'thread_wt0OPSu5PoKFvZ9kqkjYcW72', 'thread_nh1ToLIgM1YpeeH79XGGlhUk', 'thread_sZwBrsrrot9EPYU0OX4zIITL']

threads_ids_20_20 = ['thread_mJWBXXCpCom1eSNA6XhRTZLg', 'thread_trE6AAsIQvBfjKZxeQazlRO4', 'thread_O4liSpFwTFNWDtavQR1ym8yM', 'thread_uWVXwawkRk0BI5LbsYdlHmuX', 'thread_FRbRZkBCBsciG6YFlp1iWZuO', 'thread_NiOWYeZI9EnFOOqqMDF3hmc4', 'thread_RAgpFAL2zXTdWqpxYURwqAs7', 'thread_Doj4MfIMRdyIwjeEU3cj8Jym', 'thread_2incj7vAaTNylnfAmu2N47iw', 'thread_LdmL44uifahzeFEKTEuBl4S5']

threads_ids_721_721 = ['thread_OO6uiA73is3SwaWZaWkGPKce', 'thread_vrduOnqRUfXyXCiSztEYGh0A', 'thread_MSAho0w9dKwebJBhKqbnsu23', 'thread_hAY0L52fkQZRCC3cfwCWTeCH', 'thread_8XeVCLNv4MRerm1c9oJvFgfF', 'thread_TKlGTYW8STVTa7PVqwNrNPwz', 'thread_Xu5VeImMkiZBKRjG7m6kw4Dm', 'thread_uBun5yVx2Yz2YogSCGYGO0sm', 'thread_qXqiZ9HsIyVSM4Uwk6WoxHfX', 'thread_kZsnsgJcbCuria5izeb6pTrP']

threads_ids_721_20_1155 = ['thread_fCbfNXjS7jmsyOkGvFHF6vz2', 'thread_K31nh3BqGH0WZUa3qBpynrVh', 'thread_zF6DCRAN2x41vXGfnSbEeV0t', 'thread_6w1xHtb05GWCwOgxX6bu3ZG6', 'thread_SRFKvyTliRO7Be3qH37CehhE', 'thread_aouJurVboq0QCEQ1nDUWkgFs', 'thread_Yt2a7VFCPjlq0VyEPTL0T1N9', 'thread_AYpJ5mYWx7LGaLLy6rQxzmKK', 'thread_FbvDgewZZd6776Qp9MKEBTdb', 'thread_2y7wUoREnEovNUmACmzn0gkz']

threads_ids_721_1155 = ['thread_yw2bBWuuRKYQcQHhaPJUyXw7', 'thread_MIu6Cy3eBrtxfnCtWm4RH7jS', 'thread_fELOj7CnWIN1u0vR9etfiuM3', 'thread_NHhytidAetdeNIv35cUT1whz', 'thread_l4wMEQhYMPYAeHcrooz6dk2v', 'thread_8qmKMzk0wsuvtEUYdgkh11x6', 'thread_AgCdoUV0PkNdmwhim2SOs72P', 'thread_nH8Q4FHMlTWXmxcIXcJDohoA', 'thread_OYt0K6gyh26gLjpLg7Ykw11d', 'thread_pChp5OuRqkewav6YmjVXxcr3']

threads_ids_721 = ['thread_zV4aAsOaiipaZQIPsVPYSMkX', 'thread_XvA5R0Uw2byLH7ggxL0YVVdp', 'thread_t8McWHQXM5BZX4Igxqgi5Q1u', 'thread_UVgy5idmY5DnsCHyVgbiH8Ng', 'thread_4BWxzlVDNpdHEH0GEutuCK8u', 'thread_3vdJru4dIwtMue5IQzywk7kB', 'thread_ak0DaJmaMBuha8ko7HFJcJMF', 'thread_jeP0geUsMh6veALbQlrWyltN', 'thread_l09gIAReTaqg34idoV0OfF5Q', 'thread_zV4aAsOaiipaZQIPsVPYSMkX']

threads_ids_20_1155 = ['thread_t87sPGDBp0c7BDziOqX1wJs5', 'thread_jZwVvSMT0XMgxmXA9d0dYugb', 'thread_ESekwBtIJEwpmYNywf9kbDOR', 'thread_niwp5sNIZkb6P5Q3fgYCwDOo', 'thread_EtkOYoq9SCVw874A5ImaejQ7', 'thread_9T3XyAnSVpFL89ubYSyFb7YR', 'thread_c7Zxz9rPBy8rIuixiLlWh5dE', 'thread_fqVAMuLVrGurGmHf7tytiBPV', 'thread_tokROLa21rReJy6lh10x09T2', 'thread_U3uGRIFsrestQXp5yeSI8xVc']

threads_ids_20_721_1155 = ['thread_6yMAb6s6hJ4pI2HQ07XvGyjd', 'thread_VRHaGwIQF4Qp9zTnRrj1UGnL', 'thread_wqlypVcSws1oF5cLxP0DPi81', 'thread_awSqOeq22tLLEVa1EBk8Ihjg', 'thread_HCS5BADbSl7doyrnpijfNUQR', 'thread_7suyBwkU3q67WzJcBI7tsOsR', 'thread_7yeMED9pO4zBFpotyfSfLp10', 'thread_AkjYVItu9cg5lKXD8gsPUQox', 'thread_EuYkTaVDHrkY5VweX38hdxjg', 'thread_nL1XeOfPjuHGntexxgBYCWwl']

for thread_id in threads_ids_20_721_1155:
    fetch_and_save_thread(thread_id, f"{thread_id}.txt")
