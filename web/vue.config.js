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
  publicPath: "/static/",
  chainWebpack: config => {
    config
      .plugin('html')
      .tap(args => {
        args[0].title = "Mod-Kt";
        return args;
      })
  }
}