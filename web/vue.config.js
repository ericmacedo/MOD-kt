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
}