const path = require("path");
const webpack = require("webpack");

module.exports = {
  mode: "production",  // Explicitly setting the mode to production
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "static/js"),
    filename: "bundle.js",  // Static file name for single entry
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
    ],
  },
  optimization: {
    minimize: true,
  },
  plugins: [
    // new webpack.DefinePlugin({
    //   "process.env": {
    //     NODE_ENV: JSON.stringify("production"),
    //   },
    // }),
  ],
  devtool: "source-map",  // Add source maps for easier debugging
};
