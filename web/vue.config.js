module.exports = {
  runtimeCompiler: true,
  configureWebpack: {
    optimization: {
      splitChunks: {
        maxSize: 1048576
      }
    }
  },
  productionSourceMap: false,
  publicPath: `${process.env.VUE_APP_SERVER_PREFIX || ""}/static/`,
  chainWebpack: config => {
    config
      .plugin('html')
      .tap(args => {
        args[0].title = "Mod-Kt";
        return args;
      })
  }
}
