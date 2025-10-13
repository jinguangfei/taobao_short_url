fetch("https://h5api.m.taobao.com/h5/mtop.taobao.third.pcdetail.data.get/1.0/?jsv=2.7.2&appKey=12574478&t=1760313876104&sign=e658f3f39bc53db03f0a917a7b83923e&api=mtop.taobao.third.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&dataType=json&valueType=string&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=json&data=%7B%22id%22%3A%22802554908362%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%220000fZTFNrPJcKylO8zAsxrOaWGLY-3P8dLT6Anf5h8-XGY%22%2C%22exParams%22%3A%22%7B%5C%22from%5C%22%3A%5C%22cart%5C%22%2C%5C%22id%5C%22%3A%5C%22802554908362%5C%22%2C%5C%22skuId%5C%22%3A%5C%225759433006562%5C%22%2C%5C%22upStreamPrice%5C%22%3A%5C%2265300%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22from%3Dcart%26id%3D802554908362%26skuId%3D5759433006562%26upStreamPrice%3D65300%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fcart.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2F%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22Cart%5C%22%7D%22%7D", {
    "headers": {
      "accept": "application/json",
      "accept-language": "zh-CN,zh;q=0.9",
      "content-type": "application/x-www-form-urlencoded",
      "priority": "u=1, i",
      "sec-ch-ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "\"macOS\"",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-site"
    },
    "referrer": "https://cart.taobao.com/?spm=pc_detail.30350276.20220530.2.39db7dd626U9bW",
    "body": null,
    "method": "GET",
    "mode": "cors",
    "credentials": "include"
  }).then(res => res.json()).then(data => console.log(data))