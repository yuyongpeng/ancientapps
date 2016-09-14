ancientapps
===========
apache config
<VirtualHost inhouse-test.bbwc.cn:80>                                                                                                                
    ServerName inhouse-test.bbwc.cn
    WSGIDaemonProcess ancientapps user=www-data group=www-data threads=5
    WSGIScriptAlias / /home/ubuntu/1-APPS/ancientapps/run.wsgi
    <Directory /home/ubuntu/1-APPS/ancientapps>
    RewriteEngine on                 
    RewriteBase /                    
    RewriteCond %{SERVER_PORT} !^443$
    RewriteRule ^.*$ https://%{SERVER_NAME}%{REQUEST_URI} [L,R]
    AllowOverride all                
       WSGIProcessGroup ancientapps 
       WSGIApplicationGroup %{GLOBAL}
    WSGIScriptReloading On           
       Order deny,allow             
       Allow from all               
    </Directory>                     
    ErrorLog ${APACHE_LOG_DIR}/ancientapps-error.log
    LogLevel info                    
    CustomLog ${APACHE_LOG_DIR}/ancientapps-access.log combined
</VirtualHost>                       
<VirtualHost *:443>                  
    ServerName inhouse-test.bbwc.cn  
    SSLEngine on                     
    SSLCertificateKeyFile /etc/apache2/ssl/bbwc.cn.key.nopass
    SSLCertificateFile /etc/apache2/ssl/STAR_bbwc_cn.crt
    SSLCertificateChainFile /etc/apache2/ssl/STAR_bbwc_cn.ca-bundle
    WSGIDaemonProcess ancientappsssl user=www-data group=www-data threads=5
    WSGIScriptAlias / /home/ubuntu/1-APPS/ancientapps/run.wsgi
    <Directory /home/ubuntu/1-APPS/ancientapps>
       WSGIProcessGroup ancientapps 
       WSGIApplicationGroup %{GLOBAL}
    WSGIScriptReloading On           
       Order deny,allow             
       Allow from all               
    </Directory>                     
    ErrorLog ${APACHE_LOG_DIR}/ancientapps-error.log
    LogLevel info                    
    CustomLog ${APACHE_LOG_DIR}/ancientapps-access.log combined
</VirtualHost>    
