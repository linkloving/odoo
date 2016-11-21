# -*- coding: utf-8 -*-
import threading
import time

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp import tools
from openerp.addons.base.ir.ir_mail_server import extract_rfc2822_addresses, _logger, _test_logger, \
    MailDeliveryException
from openerp.osv import osv

class res_company_mail(models.Model):
    _inherit = 'res.company'

    mail_auth_password = fields.Char(u'邮箱授权码')
    send_mail_server_id = fields.Many2one('ir.mail_server', string=u'发件邮箱类型')
    # rec_mail_server_id = fields.Many2one('fetchmail.server', string='收件邮箱类型')


class res_user(models.Model):
    _inherit = 'res.users'

    mail_auth_password = fields.Char(u'邮箱授权码')
    send_mail_server_id = fields.Many2one('ir.mail_server', string=u'发件邮箱类型')
    # rec_mail_server_id = fields.Many2one('fetchmail.server', string='收件邮箱类型')


# class ir_mail_server(models.Model):
#     _inherit = "ir.mail_server"
#
#     user_id = fields.Many2one('res.users', string="Owner")
#     email_name = fields.Char('Email Name', help="Overrides default email name")
#     force_use = fields.Boolean('Force Use', help="If checked and this server is chosen to send mail message, It will ignore owners mail server")
#
#     @api.model
#     def replace_email_name(self, old_email):
#         """
#         Replaces email name if new one is provided
#         """
#         if self.email_name:
#             old_name, email = parseaddr(old_email)
#             return formataddr((self.email_name, email))
#         else:
#             return old_email

class linkloving_mail_mail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        ir_mail_server_obj = self.env['ir.mail_server']
        # res_user_obj = self.env['res.users']
        for email in self:
                user = self.env.user#res_user_obj.search([('partner_id', '=', email.author_id.id)], limit=1)
                if user:
                    mail_server = self._get_mail_server()
                    #ir_mail_server_obj.search([('user_id', '=', user.id)], limit=1)
                    from_rfc2822 = extract_rfc2822_addresses(email.email_from)[-1]
                    #
                    company_id = self.env['res.company'].search([('email', '=', from_rfc2822)])
                    if mail_server:
                        if company_id:
                            if company_id.mail_auth_password:
                                mail_server.smtp_user = from_rfc2822
                                mail_server.smtp_pass = company_id.mail_auth_password
                            else:
                                raise osv.except_osv(
                                    _("Can`t find any smtp server"),
                                    _("请管理员进入“设置－公司”并设置“邮箱授权码”，以保证能正常使用邮箱功能"))
                        else:
                            if user.mail_auth_password:
                                mail_server.smtp_user = user.login
                                mail_server.smtp_pass = user.mail_auth_password
                            else:
                                raise osv.except_osv(
                                    _("Can`t find any smtp server"),
                                    _("请进入“首选项”并设置“邮箱授权码”，以保证能正常使用邮箱功能"))
                        email.mail_server_id = mail_server.id

                            # email.email_from = email.mail_server_id.replace_email_name(email.email_from)

        return super(linkloving_mail_mail, self).send(auto_commit=False, raise_exception=False)

    def _get_mail_server(self):

        mail_server = None
        if self.env.user.send_mail_server_id:
            mail_server_ids = self.env['ir.mail_server'].search(['|',('id', '=', self.env.user.send_mail_server_id.id),('id', '=', self.env.user.company_id.send_mail_server_id.id)], order='sequence', limit=1)
        else:
            raise osv.except_osv(
                _("Can`t find any smtp server"),
                _("请进入“首选项”并设置“发送邮箱类型”，以保证能正常使用邮箱功能"))
        # if mail_server_ids:
        #     mail_server = self.browse(mail_server_ids[0])

        # if mail_server:
        #     smtp_server = mail_server.smtp_host
        #     smtp_port = mail_server.smtp_port
        #     smtp_encryption = mail_server.smtp_encryption
        #     smtp_debug =  mail_server.smtp_debug

        return mail_server_ids[0]

class ir_mail_server(models.Model):
        _inherit = 'ir.mail_server'

        @api.model
        def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None, smtp_user=None,
                       smtp_password=None, smtp_encryption=None, smtp_debug=False, context=None):
            from_rfc2822 = extract_rfc2822_addresses(message['From'])[-1]
            server_id = self.env['ir.mail_server'].search(['|',('id', '=', self.env.user.send_mail_server_id.id),('id', '=', self.env.user.company_id.send_mail_server_id.id)], order='sequence', limit=1)
            #.search( [('smtp_user', '=', from_rfc2822)],)
            if server_id and server_id[0]:
                message['Return-Path'] = from_rfc2822

            smtp_from = message['Return-Path']
            if not smtp_from:
                smtp_from = self._get_default_bounce_address(context=context)
            if not smtp_from:
                smtp_from = message['From']
            assert smtp_from, "The Return-Path or From header is required for any outbound email"

            # The email's "Envelope From" (Return-Path), and all recipient addresses must only contain ASCII characters.
            from_rfc2822 = extract_rfc2822_addresses(smtp_from)
            assert from_rfc2822, ("Malformed 'Return-Path' or 'From' address: %r - "
                                  "It should contain one valid plain ASCII email") % smtp_from
            # use last extracted email, to support rarities like 'Support@MyComp <support@mycompany.com>'
            smtp_from = from_rfc2822[-1]
            email_to = message['To']
            email_cc = message['Cc']
            email_bcc = message['Bcc']

            smtp_to_list = filter(None, tools.flatten(map(extract_rfc2822_addresses, [email_to, email_cc, email_bcc])))
            assert smtp_to_list, self.NO_VALID_RECIPIENT

            x_forge_to = message['X-Forge-To']
            if x_forge_to:
                # `To:` header forged, e.g. for posting on mail.groups, to avoid confusion
                del message['X-Forge-To']
                del message['To']  # avoid multiple To: headers!
                message['To'] = x_forge_to

            # Do not actually send emails in testing mode!
            if getattr(threading.currentThread(), 'testing', False):
                _test_logger.info("skip sending email in test mode")
                return message['Message-Id']

            # Get SMTP Server Details from Mail Server
            mail_server = None
            if mail_server_id:
                mail_server = self.browse(mail_server_id)
            elif not smtp_server:
                mail_server_ids = self.search( [], order='sequence', limit=1)
                if mail_server_ids:
                    mail_server = self.browse( mail_server_ids[0])

            if mail_server:
                smtp_server = mail_server.smtp_host
                smtp_user = mail_server.smtp_user
                smtp_password = mail_server.smtp_pass
                smtp_port = mail_server.smtp_port
                smtp_encryption = mail_server.smtp_encryption
                smtp_debug = smtp_debug or mail_server.smtp_debug
            else:
                # we were passed an explicit smtp_server or nothing at all
                smtp_server = smtp_server or tools.config.get('smtp_server')
                smtp_port = tools.config.get('smtp_port', 25) if smtp_port is None else smtp_port
                smtp_user = smtp_user or tools.config.get('smtp_user')
                smtp_password = smtp_password or tools.config.get('smtp_password')
                if smtp_encryption is None and tools.config.get('smtp_ssl'):
                    smtp_encryption = 'starttls'  # STARTTLS is the new meaning of the smtp_ssl flag as of v7.0

            if not smtp_server:
                raise osv.except_osv(
                    _("Missing SMTP Server"),
                    _("Please define at least one SMTP server, or provide the SMTP parameters explicitly."))

            try:
                message_id = message['Message-Id']

                # Add email in Maildir if smtp_server contains maildir.
                if smtp_server.startswith('maildir:/'):
                    from mailbox import Maildir
                    maildir_path = smtp_server[8:]
                    mdir = Maildir(maildir_path, factory=None, create=True)
                    mdir.add(message.as_string(True))
                    return message_id

                smtp = None
                try:
                    smtp = self.connect(smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption or False,
                                        smtp_debug)
                    smtp.sendmail(smtp_from, smtp_to_list, message.as_string())
                finally:
                    if smtp is not None:
                        smtp.quit()
            except Exception, e:
                msg = _("Mail delivery failed via SMTP server '%s'.\n%s: %s, Please check your mail setting") % (tools.ustr(smtp_server),
                                                                                 e.__class__.__name__,
                                                                                 tools.ustr(e))
                raise osv.except_osv(
                    _("Mail Delivery Failed"),
                    msg)
                # raise MailDeliveryException(_("Mail Delivery Failed"), msg)
            return message_id
            # return super(ir_mail_server, self).send_email( message, mail_server_id, smtp_server, smtp_port,
            #                                               smtp_user, smtp_password, smtp_encryption, smtp_debug,
            #                                               context=context)





#接收服务器

MAX_POP_MESSAGES = 50

class linkloving_fetchmail_server(models.Model):
    _inherit = 'fetchmail.server'


    def fetch_mail(self, cr, uid, ids, context=None):
        """WARNING: meant for cron usage only - will commit() after each email!"""
        context = dict(context or {})
        context['fetchmail_cron_running'] = True
        mail_thread = self.pool.get('mail.thread')
        action_pool = self.pool.get('ir.actions.server')

        for server in self.browse(cr, uid, ids, context=context):
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            server.user = user.login
            server.password = user.mail_auth_password
            _logger.info('start checking for new emails on %s server %s', server.type, server.name)
            context.update({'fetchmail_server_id': server.id, 'server_type': server.type})
            count, failed = 0, 0
            imap_server = False
            pop_server = False
            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = mail_thread.message_process(cr, uid, server.object_id.model,
                                                                 data[0][1],
                                                                 save_original=server.original,
                                                                 strip_attachments=(not server.attach),
                                                                 context=context)
                        except Exception:
                            _logger.exception('Failed to process mail from %s server %s.', server.type, server.name)
                            failed += 1
                        if res_id and server.action_id:
                            action_pool.run(cr, uid, [server.action_id.id],
                                            {'active_id': res_id, 'active_ids': [res_id],
                                             'active_model': context.get("thread_model", server.object_id.model)})
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.type,
                                 server.name, (count - failed), failed)
                except Exception:
                    _logger.exception("General failure when trying to fetch mail from %s server %s.", server.type,
                                      server.name)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif server.type == 'pop':
                try:
                    while True:
                        pop_server = server.connect()
                        (numMsgs, totalSize) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, numMsgs) + 1):
                            (header, msges, octets) = pop_server.retr(num)
                            msg = '\n'.join(msges)
                            res_id = None
                            try:
                                res_id = mail_thread.message_process(cr, uid, server.object_id.model,
                                                                     msg,
                                                                     save_original=server.original,
                                                                     strip_attachments=(not server.attach),
                                                                     context=context)
                                pop_server.dele(num)
                            except Exception:
                                _logger.exception('Failed to process mail from %s server %s.', server.type, server.name)
                                failed += 1
                            if res_id and server.action_id:
                                action_pool.run(cr, uid, [server.action_id.id],
                                                {'active_id': res_id, 'active_ids': [res_id],
                                                 'active_model': context.get("thread_model", server.object_id.model)})
                            cr.commit()
                        if numMsgs < MAX_POP_MESSAGES:
                            break
                        pop_server.quit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", numMsgs,
                                     server.type, server.name, (numMsgs - failed), failed)
                except Exception:
                    _logger.exception("General failure when trying to fetch mail from %s server %s.", server.type,
                                      server.name)
                finally:
                    if pop_server:
                        pop_server.quit()
            server.write({'date': time.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)})
        return super(linkloving_fetchmail_server, self).fetch_mail(cr,uid,ids,context)


