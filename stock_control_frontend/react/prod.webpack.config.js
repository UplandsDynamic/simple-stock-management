const path = require("path");
const BundleTracker = require('webpack-bundle-tracker');
const statsFileURL = './webpack-stats.json';
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const webpack = require('webpack');

module.exports = {

    context: __dirname,

    mode: 'production',

    devtool: "source-map",

    entry: {
        main: './assets/js/index.jsx',
        data: './assets/js/data-table.jsx',
        api: './assets/js/api-request.jsx',
        modal: './assets/js/stock-update-modal.jsx'
    },

    output: {
        path: path.resolve(__dirname, 'assets/bundles/'),
        filename: '[name]-[hash].js',
        chunkFilename: '[name]-[hash].js'
    },

    resolve: {
        extensions: [".jsx", ".js"]
    },

    optimization: {
        namedModules: true, // NamedModulesPlugin()
        splitChunks: { // CommonsChunkPlugin()
            name: 'vendor',
            minChunks: 2
        },
        noEmitOnErrors: true, // NoEmitOnErrorsPlugin
        concatenateModules: true //ModuleConcatenationPlugin
    },

    plugins: [
        new BundleTracker({filename: statsFileURL}),
        new MiniCssExtractPlugin({
            // Options similar to the same options in webpackOptions.output
            // both options are optional
            filename: '[name]-[hash].css',
            chunkFilename: '[id].css'
        }),
        new BundleAnalyzerPlugin({'analyzerMode': 'disabled'}),  // server|static|disabled
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
    ],

    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {}
                }
            }, {
                test: /\.jsx$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {}
                }
            },
            {
                test: /\.(png|woff|woff2|eot|ttf|svg)$/,
                use: {
                    loader: 'url-loader?limit=100000'
                }
            },
            {
                test: /\.css$/,
                use:
                    [
                        {
                            loader: MiniCssExtractPlugin.loader,
                            options: {}
                        },
                        'css-loader'
                    ]
            }

        ]
    }
};